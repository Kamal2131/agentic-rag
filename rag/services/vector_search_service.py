"""
Vector Search Service using Qdrant for similarity search.
"""

from rag.models import Document
from rag.services.embedding_service import EmbeddingService
from rag.services.qdrant_service import QdrantService


class VectorSearchService:
    """
    Service for performing vector similarity search on documents.
    """
    
    def __init__(self):
        """Initialize the vector search service."""
        self.embedding_service = EmbeddingService()
        self.qdrant_service = QdrantService()
    
    def search(self, query, top_k=5, filters=None):
        """
        Search for documents similar to the query.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            list: List of documents with similarity scores
        """
        # Generate query embedding
        query_embedding = self.embedding_service.embed(query)
        
        # Perform vector search in Qdrant
        qdrant_results = self.qdrant_service.search_vectors(
            query_embedding=query_embedding,
            top_k=top_k,
            filters=filters
        )
        
        # Fetch full document data from database
        results = []
        for hit in qdrant_results:
            try:
                doc = Document.objects.get(id=hit['id'])
                results.append({
                    'id': str(doc.id),
                    'title': doc.title,
                    'content': doc.content,
                    'metadata': doc.metadata,
                    'score': hit['score'],
                })
            except Document.DoesNotExist:
                continue
        
        return results
