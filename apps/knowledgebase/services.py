"""
Document Service for managing document operations.
"""

from apps.knowledgebase.models import Document
from apps.core.services import EmbeddingService
from apps.vectorstore.services import QdrantService
import pypdf
import io
import uuid

class DocumentService:
    """
    Service for document management including creation and embedding.
    """
    
    def __init__(self):
        """Initialize the document service."""
        self.embedding_service = EmbeddingService()
        self.qdrant_service = QdrantService()

    def process_pdf(self, file_obj, title, metadata=None):
        """
        Process a PDF file: extract text, chunk, embed, and store.
        
        Args:
            file_obj: File-like object containing PDF data
            title: Document title
            metadata: Optional metadata dict
            
        Returns:
            Document: Created document instance
        """
        # 1. Extract text from PDF
        pdf_reader = pypdf.PdfReader(file_obj)
        text_content = ""
        for page in pdf_reader.pages:
            text_content += page.extract_text() + "\n"
            
        # 2. Create Document record
        document = Document.objects.create(
            title=title,
            content=text_content,
            metadata=metadata or {}
        )
        
        # 3. Chunk text (simple chunking by characters for now)
        # In a real app, use a proper tokenizer or recursive splitter
        chunk_size = 1000
        overlap = 200
        chunks = []
        
        for i in range(0, len(text_content), chunk_size - overlap):
            chunk = text_content[i:i + chunk_size]
            if len(chunk) < 5:  # Skip very small chunks
                continue
            chunks.append(chunk)
            
        # 4. Generate embeddings for chunks
        embeddings = self.embedding_service.embed_batch(chunks)
        
        # 5. Prepare batch for Qdrant
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = uuid.uuid4()
            points.append({
                'id': chunk_id,
                'vector': embedding,
                'payload': {
                    'document_id': str(document.id),
                    'chunk_index': i,
                    'content': chunk,
                    'title': title,
                    **(metadata or {})
                }
            })
            
        # 6. Store in Qdrant
        if points:
            self.qdrant_service.upsert_batch(points)
            
        return document
    
    def create_document(self, title, content, metadata=None):
        """
        Create a new document with embedding.
        
        Args:
            title: Document title
            content: Document content
            metadata: Optional metadata dict
            
        Returns:
            Document: Created document instance
        """
        # Generate embedding for content
        embedding = self.embedding_service.embed(content)
        
        # Create document in database
        document = Document.objects.create(
            title=title,
            content=content,
            metadata=metadata or {}
        )
        
        # Store embedding in Qdrant
        self.qdrant_service.upsert_vector(
            document_id=document.id,
            embedding=embedding,
            metadata={
                'title': title,
                **(metadata or {})
            }
        )
        
        return document
    
    def update_document(self, document_id, title=None, content=None, metadata=None):
        """
        Update an existing document.
        
        Args:
            document_id: Document ID
            title: Optional new title
            content: Optional new content
            metadata: Optional new metadata
            
        Returns:
            Document: Updated document instance
        """
        document = Document.objects.get(id=document_id)
        
        if title:
            document.title = title
        if content:
            document.content = content
            # Regenerate embedding if content changed
            embedding = self.embedding_service.embed(content)
            self.qdrant_service.upsert_vector(
                document_id=document.id,
                embedding=embedding,
                metadata={
                    'title': document.title,
                    **(metadata or document.metadata)
                }
            )
        if metadata is not None:
            document.metadata = metadata
        
        document.save()
        return document
    
    def delete_document(self, document_id):
        """
        Delete a document.
        
        Args:
            document_id: Document ID to delete
        """
        # Delete from Qdrant
        self.qdrant_service.delete_vector(document_id)
        
        # Delete from database
        Document.objects.filter(id=document_id).delete()
    
    def get_document(self, document_id):
        """
        Get a document by ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            Document: Document instance
        """
        return Document.objects.get(id=document_id)
    
    def list_documents(self, limit=100, offset=0):
        """
        List documents with pagination.
        
        Args:
            limit: Number of documents to return
            offset: Offset for pagination
            
        Returns:
            QuerySet: Documents queryset
        """
        return Document.objects.all()[offset:offset+limit]
