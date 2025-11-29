import pytest
from apps.rag.models import Document, ChatHistory, ToolLog


@pytest.mark.django_db
class TestDocumentModel:
    """Test Document model."""

    def test_create_document(self):
        """Test creating a document."""
        doc = Document.objects.create(
            title="Test Document",
            content="This is test content",
            metadata={"source": "test"}
        )
        assert doc.id is not None
        assert doc.title == "Test Document"
        assert doc.content == "This is test content"
        assert doc.metadata == {"source": "test"}

    def test_document_str(self):
        """Test document string representation."""
        doc = Document.objects.create(title="Test Doc", content="Content")
        assert str(doc) == "Test Doc"

    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires PostgreSQL pg_trgm extension")
    def test_keyword_search(self, create_document):
        """Test keyword search functionality."""
        create_document(title="Python Programming", content="Learn Python basics")
        create_document(title="Java Guide", content="Java fundamentals")
        
        results = Document.keyword_search("Python")
        assert results.count() >= 1


@pytest.mark.django_db
class TestChatHistoryModel:
    """Test ChatHistory model."""

    def test_create_chat_history(self):
        """Test creating chat history."""
        chat = ChatHistory.objects.create(
            user="test_user",
            messages=[
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi!"}
            ]
        )
        assert chat.id is not None
        assert chat.user == "test_user"
        assert len(chat.messages) == 2

    def test_chat_history_str(self):
        """Test chat history string representation."""
        chat = ChatHistory.objects.create(user="john", messages=[])
        assert "john" in str(chat)


@pytest.mark.django_db
class TestToolLogModel:
    """Test ToolLog model."""

    def test_create_tool_log(self):
        """Test creating tool log."""
        log = ToolLog.objects.create(
            tool_name="vector_search",
            input_data={"query": "test"},
            output_data={"results": []}
        )
        assert log.id is not None
        assert log.tool_name == "vector_search"
        assert log.input_data == {"query": "test"}

    def test_tool_log_str(self):
        """Test tool log string representation."""
        log = ToolLog.objects.create(
            tool_name="test_tool",
            input_data={},
            output_data={}
        )
        assert "test_tool" in str(log)
