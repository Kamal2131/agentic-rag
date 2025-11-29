"""
Vector Store Services.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from django.conf import settings
import uuid

class QdrantService:
    """
    Service for managing Qdrant vector database operations.
    """
    
    COLLECTION_NAME = "documents"
    
    def __init__(self):
        """Initialize Qdrant client."""
        self.client = QdrantClient(
            host=settings.QDRANT_CONFIG['HOST'],
            port=settings.QDRANT_CONFIG['PORT']
        )
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Ensure the documents collection exists."""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if self.COLLECTION_NAME not in collection_names:
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=settings.EMBEDDING_CONFIG['EMBEDDING_DIMENSION'],
                    distance=Distance.COSINE
                )
            )
    
    def upsert_vector(self, document_id, embedding, metadata=None):
        """
        Insert or update a document vector.
        
        Args:
            document_id: UUID of the document
            embedding: Vector embedding
            metadata: Optional metadata dict
            
        Returns:
            bool: Success status
        """
        try:
            point = PointStruct(
                id=str(document_id),
                vector=embedding,
                payload=metadata or {}
            )
            
            self.client.upsert(
                collection_name=self.COLLECTION_NAME,
                points=[point]
            )
            return True
        except Exception as e:
            raise Exception(f"Failed to upsert vector: {str(e)}")
    
    def upsert_batch(self, points):
        """
        Insert or update multiple document vectors.
        
        Args:
            points: List of dictionaries with 'id', 'vector', and 'payload'
            
        Returns:
            bool: Success status
        """
        try:
            batch_points = [
                PointStruct(
                    id=str(p['id']),
                    vector=p['vector'],
                    payload=p.get('payload', {})
                ) for p in points
            ]
            
            self.client.upsert(
                collection_name=self.COLLECTION_NAME,
                points=batch_points
            )
            return True
        except Exception as e:
            raise Exception(f"Failed to batch upsert vectors: {str(e)}")
    
    def search_vectors(self, query_embedding, top_k=5, filters=None):
        """
        Search for similar vectors.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results
            filters: Optional metadata filters
            
        Returns:
            list: Search results with scores
        """
        try:
            search_result = self.client.search(
                collection_name=self.COLLECTION_NAME,
                query_vector=query_embedding,
                limit=top_k,
                query_filter=filters
            )
            
            results = []
            for hit in search_result:
                results.append({
                    'id': hit.id,
                    'score': hit.score,
                    'payload': hit.payload
                })
            
            return results
        except Exception as e:
            raise Exception(f"Vector search failed: {str(e)}")
    
    def delete_vector(self, document_id):
        """
        Delete a document vector.
        
        Args:
            document_id: UUID of the document
        """
        try:
            self.client.delete(
                collection_name=self.COLLECTION_NAME,
                points_selector=[str(document_id)]
            )
        except Exception as e:
            raise Exception(f"Failed to delete vector: {str(e)}")
