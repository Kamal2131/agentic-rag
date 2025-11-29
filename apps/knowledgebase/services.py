"""
Document Service for managing document operations.
"""

from apps.knowledgebase.models import Document
from apps.core.services import EmbeddingService
from apps.vectorstore.services import QdrantService

class DocumentService:
    """
    Service for document management including creation and embedding.
    """
    
    def __init__(self):
        """Initialize the document service."""
        self.embedding_service = EmbeddingService()
        self.qdrant_service = QdrantService()
    
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
