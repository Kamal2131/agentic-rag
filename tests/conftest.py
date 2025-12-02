import pytest
from django.conf import settings


@pytest.fixture(scope="session")
def django_db_setup():
    """Configure test database."""
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "ATOMIC_REQUESTS": False,
    }


@pytest.fixture
def api_client():
    """Return DRF API test client."""
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def create_document():
    """Factory fixture for creating Document instances."""
    from apps.knowledgebase.models import Document

    def _create_document(title="Test Document", content="Test content"):
        return Document.objects.create(title=title, content=content, metadata={"source": "test"})

    return _create_document


@pytest.fixture
def create_chat_history():
    """Factory fixture for creating ChatHistory instances."""
    from apps.rag.models import ChatHistory

    def _create_chat_history(user="test_user", messages=None):
        if messages is None:
            messages = [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
            ]
        return ChatHistory.objects.create(user=user, messages=messages)

    return _create_chat_history


@pytest.fixture
def create_tool_log():
    """Factory fixture for creating ToolLog instances."""
    from apps.rag.models import ToolLog

    def _create_tool_log(tool_name="test_tool", input_data=None, output_data=None):
        return ToolLog.objects.create(
            tool_name=tool_name,
            input_data=input_data or {"test": "input"},
            output_data=output_data or {"test": "output"},
        )

    return _create_tool_log


@pytest.fixture
def mock_openai_response(monkeypatch):
    """Mock OpenAI API responses."""

    class MockResponse:
        def __init__(self, data):
            self.data = data
            self.choices = [
                type("obj", (object,), {"message": type("obj", (object,), {"content": data})()})()
            ]

    def mock_create(*args, **kwargs):
        return MockResponse('{"thought": "test", "final_answer": "Test response"}')

    from unittest.mock import Mock

    mock_client = Mock()
    mock_client.chat.completions.create = mock_create

    return mock_client
