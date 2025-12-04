"""
Web Search Tool using Serper.dev API.
"""

from apps.core.tools.serper import SerperDevTool


def web_search_tool(query):
    """
    Search the web for information using Serper API.

    Args:
        query (str): Search query

    Returns:
        dict: Search results with organic results from Google
    """
    serper = SerperDevTool()

    try:
        results = serper.search(query)

        # Handle error response
        if "error" in results:
            return {
                "success": False,
                "results": [],
                "count": 0,
                "message": f"Web search error: {results['error']}",
            }

        # Extract organic results
        organic_results = results.get("organic", [])

        # Format results for the RAG pipeline
        formatted_results = [
            {
                "title": result.get("title", ""),
                "content": result.get("snippet", ""),
                "url": result.get("link", ""),
            }
            for result in organic_results[:5]  # Limit to top 5 results
        ]

        return {
            "success": True,
            "results": formatted_results,
            "count": len(formatted_results),
            "message": "Web search completed successfully",
        }

    except Exception as e:
        return {
            "success": False,
            "results": [],
            "count": 0,
            "message": f"Web search failed: {str(e)}",
        }


# Tool metadata
TOOL_METADATA = {
    "name": "web_search",
    "description": "Search the web for up-to-date information using Google via Serper API",
    "parameters": {
        "query": {"type": "string", "description": "The search query", "required": True}
    },
}
