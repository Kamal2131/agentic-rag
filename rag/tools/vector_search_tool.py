"""
Vector Search Tool for the agent.
"""

from rag.services.vector_search_service import VectorSearchService


def vector_search_tool(query, top_k=5, filters=None):
    """
    Search for relevant documents using vector similarity.
    
    Args:
        query (str): Search query text
        top_k (int): Number of results to return (default: 5)
        filters (dict): Optional metadata filters
        
    Returns:
        dict: Search results with documents and metadata
    """
    try:
        service = VectorSearchService()
        results = service.search(query=query, top_k=top_k, filters=filters)
        
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
    'name': 'vector_search',
    'description': 'Search for documents using semantic vector similarity',
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
            'default': 5
        },
        'filters': {
            'type': 'object',
            'description': 'Optional metadata filters',
            'required': False
        }
    }
}
