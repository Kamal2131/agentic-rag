"""
Vector Search Service using Qdrant for similarity search.
"""

from apps.knowledgebase.models import Document
from apps.rag.services.embedding_service import EmbeddingService
from apps.rag.services.qdrant_service import QdrantService


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
            query_embedding=query_embedding, top_k=top_k, filters=filters
        )

        # Process results - chunks have document_id in payload
        results = []
        seen_docs = set()  # Avoid duplicates
        
        for hit in qdrant_results:
            try:
                payload = hit.get("payload", {})
                
                # Get document_id from payload (chunks store parent document ID)
                document_id = payload.get("document_id")
                
                if not document_id:
                    # If no document_id, this might be a direct document vector
                    # Try using the hit ID itself
                    document_id = hit["id"]
                
                # Skip if we've already added this document
                if document_id in seen_docs:
                    continue
                    
                # Try to fetch the document
                try:
                    doc = Document.objects.get(id=document_id)
                    results.append(
                        {
                            "id": str(doc.id),
                            "title": doc.title,
                            "content": payload.get("content", doc.content),  # Use chunk content if available
                            "chunk_content": payload.get("content"),  # Include chunk for context
                            "metadata": doc.metadata,
                            "score": hit["score"],
                        }
                    )
                    seen_docs.add(document_id)
                except Document.DoesNotExist:
                    # Document not found, return chunk info only
                    results.append(
                        {
                            "id": str(hit["id"]),
                            "title": payload.get("title", "Unknown"),
                            "content": payload.get("content", ""),
                            "chunk_content": payload.get("content"),
                            "metadata": payload,
                            "score": hit["score"],
                        }
                    )
            except Exception as e:
                # Log error but continue processing other results
                print(f"Error processing search result: {e}")
                continue

        return results
