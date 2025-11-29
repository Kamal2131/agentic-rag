"""
Tool Registry for managing and executing agent tools.
"""

from apps.rag.tools import vector_search_tool, keyword_search_tool, sql_query_tool, web_search_tool


class ToolRegistry:
    """
    Central registry for all agent tools.
    """
    
    def __init__(self):
        """Initialize the tool registry."""
        self.tools = {
            'vector_search': {
                'function': vector_search_tool.vector_search_tool,
                'metadata': vector_search_tool.TOOL_METADATA
            },
            'keyword_search': {
                'function': keyword_search_tool.keyword_search_tool,
                'metadata': keyword_search_tool.TOOL_METADATA
            },
            'sql_query': {
                'function': sql_query_tool.sql_query_tool,
                'metadata': sql_query_tool.TOOL_METADATA
            },
            'web_search': {
                'function': web_search_tool.web_search_tool,
                'metadata': web_search_tool.TOOL_METADATA
            }
        }
    
    def call(self, tool_name, **kwargs):
        """
        Execute a tool by name.
        
        Args:
            tool_name (str): Name of the tool to execute
            **kwargs: Arguments to pass to the tool
            
        Returns:
            dict: Tool execution result
        """
        if tool_name not in self.tools:
            return {
                'success': False,
                'error': f'Unknown tool: {tool_name}',
                'available_tools': list(self.tools.keys())
            }
        
        try:
            tool_function = self.tools[tool_name]['function']
            result = tool_function(**kwargs)
            return result
        except Exception as e:
            return {
                'success': False,
                'error': f'Tool execution failed: {str(e)}'
            }
    
    def get_tool_descriptions(self):
        """
        Get descriptions of all available tools.
        
        Returns:
            dict: Tool metadata for all tools
        """
        descriptions = {}
        for tool_name, tool_data in self.tools.items():
            descriptions[tool_name] = tool_data['metadata']
        return descriptions
    
    def list_tools(self):
        """
        List all available tools.
        
        Returns:
            list: Names of available tools
        """
        return list(self.tools.keys())
