from apps.rag.tools.registry import ToolRegistry


class TestToolRegistry:
    """Test ToolRegistry."""

    def test_registry_has_tools(self):
        """Test that registry contains tools."""
        registry = ToolRegistry()
        tools = registry.list_tools()  # Returns list of tool names
        assert isinstance(tools, list)
        assert len(tools) > 0
        assert "vector_search" in tools

    def test_get_tool_descriptions(self):
        """Test getting tool descriptions."""
        registry = ToolRegistry()
        descriptions = registry.get_tool_descriptions()  # Returns dict of metadata
        assert isinstance(descriptions, dict)
        assert "vector_search" in descriptions
        assert "name" in descriptions["vector_search"]
        assert "description" in descriptions["vector_search"]

    def test_call_nonexistent_tool(self):
        """Test calling non-existent tool."""
        registry = ToolRegistry()
        result = registry.call("nonexistent_tool")
        assert "error" in result
        assert result["success"] is False
