"""
Keyword Search Tool for the agent.
"""

from apps.knowledgebase.models import Document


def keyword_search_tool(query, top_k=10):
    """
    Search for documents using keyword matching.
    
    Args:
        query (str): Search query text
        top_k (int): Number of results to return (default: 10)
        
    Returns:
        dict: Search results with documents
    """
    try:
        documents = Document.keyword_search(query=query, top_k=top_k)
        
        results = []
        for doc in documents:
            results.append({
                'id': str(doc.id),
                'title': doc.title,
                'content': doc.content,
                'metadata': doc.metadata,
                'similarity': float(doc.similarity) if hasattr(doc, 'similarity') else None,
            })
        
        return {
            'success': True,
            'results': results,
            'count': len(results)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'results': []
        }


# Tool metadata
TOOL_METADATA = {
    'name': 'keyword_search',
    'description': 'Search for documents using keyword matching and trigram similarity',
    'parameters': {
        'query': {
            'type': 'string',
            'description': 'The search query',
            'required': True
        },
        'top_k': {
            'type': 'integer',
            'description': 'Number of results to return',
            'required': False,
            'default': 10
        }
    }
}
