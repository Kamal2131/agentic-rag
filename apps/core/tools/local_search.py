"""
Local Search Tool for retrieving documents from knowledgebase.
"""

from apps.vectorstore.services import QdrantService
from apps.core.services import EmbeddingService
from apps.knowledgebase.models import Document

class LocalSearchTool:
    """
    Tool for searching local documents using hybrid search (Vector + Keyword).
    """
    
    def __init__(self):
        self.qdrant_service = QdrantService()
        self.embedding_service = EmbeddingService()
    
    def search(self, query, top_k=5):
        """
        Execute local search.
        
        Args:
            query (str): Search query
            top_k (int): Number of results
            
        Returns:
            list: Search results
        """
        # 1. Vector Search
        query_embedding = self.embedding_service.embed(query)
        vector_results = self.qdrant_service.search_vectors(query_embedding, top_k=top_k)
        
        # 2. Keyword Search
        keyword_results = Document.keyword_search(query, top_k=top_k)
        
        # 3. Combine Results (Simple deduplication for now)
        combined_results = []
        seen_ids = set()
        
        # Add vector results
        for res in vector_results:
            doc_id = res['id']
            if doc_id not in seen_ids:
                try:
                    doc = Document.objects.get(id=doc_id)
                    combined_results.append({
                        'id': str(doc.id),
                        'title': doc.title,
                        'content': doc.content,
                        'score': res['score'],
                        'source': 'vector'
                    })
                    seen_ids.add(doc_id)
                except Document.DoesNotExist:
                    continue
        
        # Add keyword results
        for doc in keyword_results:
            if str(doc.id) not in seen_ids:
                combined_results.append({
                    'id': str(doc.id),
                    'title': doc.title,
                    'content': doc.content,
                    'score': getattr(doc, 'similarity', 0),
                    'source': 'keyword'
                })
                seen_ids.add(str(doc.id))
        
        return combined_results[:top_k]
