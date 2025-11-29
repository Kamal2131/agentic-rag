import pytest
from apps.rag.tools.registry import ToolRegistry


class TestToolRegistry:
    """Test ToolRegistry."""

    def test_registry_has_tools(self):
        """Test that registry contains tools."""
        registry = ToolRegistry()
        tools = registry.get_all_tools()
        assert len(tools) > 0
        assert 'vector_search' in [t['name'] for t in tools]

    def test_get_tool_metadata(self):
        """Test getting tool metadata."""
        registry = ToolRegistry()
        metadata = registry.get_tool_metadata('vector_search')
        assert metadata is not None
        assert 'name' in metadata
        assert 'description' in metadata

    def test_call_nonexistent_tool(self):
        """Test calling non-existent tool."""
        registry = ToolRegistry()
        result = registry.call('nonexistent_tool')
        assert 'error' in result
