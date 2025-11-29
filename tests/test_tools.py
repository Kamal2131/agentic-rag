import pytest
from apps.rag.tools.registry import ToolRegistry


class TestToolRegistry:
    """Test ToolRegistry."""

    def test_registry_has_tools(self):
        """Test that registry contains tools."""
        registry = ToolRegistry()
        tools = registry.list_tools()
        assert len(tools) > 0
        assert 'vector_search' in [t['name'] for t in tools]

    def test_get_tool_info(self):
        """Test getting tool info."""
        registry = ToolRegistry()
        info = registry.get_tool_info('vector_search')
        assert info is not None
        assert 'name' in info
        assert 'description' in info

    def test_call_nonexistent_tool(self):
        """Test calling non-existent tool."""
        registry = ToolRegistry()
        result = registry.call('nonexistent_tool')
        assert 'error' in result
