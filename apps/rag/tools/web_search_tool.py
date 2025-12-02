"""
Web Search Tool (placeholder for future implementation).
"""


def web_search_tool(query):
    """
    Search the web for information (placeholder).

    Args:
        query (str): Search query

    Returns:
        dict: Search results (currently a placeholder)
    """
    return {
        "success": True,
        "results": [
            {
                "title": "Web search not yet implemented",
                "content": "This is a placeholder for web search functionality",
                "url": "#",
            }
        ],
        "count": 1,
        "message": "Web search functionality coming soon",
    }


# Tool metadata
TOOL_METADATA = {
    "name": "web_search",
    "description": "Search the web for information (placeholder)",
    "parameters": {
        "query": {"type": "string", "description": "The search query", "required": True}
    },
}
