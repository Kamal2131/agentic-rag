import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestToolsAPI:
    """Test tools listing API."""

    def test_list_tools(self, api_client):
        """Test listing available tools."""
        # Correct URL from router: /api/rag/tools/
        response = api_client.get('/api/rag/tools/')
        assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
class TestDocumentUploadAPI:
    """Test document upload API."""

    def test_upload_document(self, api_client, monkeypatch):
        """Test uploading a document."""
        # Mock embedding service - use correct method name
        from apps.rag.services.embedding_service import EmbeddingService
        
        def mock_embed(self, text):
            return [0.1] * 1536
        
        monkeypatch.setattr(EmbeddingService, 'embed', mock_embed)
        
        # Correct URL: /api/rag/upload/
        data = {
            'title': 'Test Document',
            'content': 'This is test content for the document.',
            'metadata': {'source': 'test'}
        }
        response = api_client.post('/api/rag/upload/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'id' in response.json()


@pytest.mark.django_db
class TestChatHistoryAPI:
    """Test chat history API."""

    def test_list_chat_history(self, api_client, create_chat_history):
        """Test listing chat history."""
        create_chat_history(user="user1")
        create_chat_history(user="user2")
        
        # Correct URL from router: /api/rag/chat-history/
        response = api_client.get('/api/rag/chat-history/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data or isinstance(data, list)

    def test_retrieve_chat_history(self, api_client, create_chat_history):
        """Test retrieving specific chat history."""
        chat = create_chat_history()
        # Correct URL from router: /api/rag/chat-history/{id}/
        response = api_client.get(f'/api/rag/chat-history/{chat.id}/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['id'] == chat.id


@pytest.mark.django_db
class TestToolLogsAPI:
    """Test tool logs API."""

    def test_list_tool_logs(self, api_client, create_tool_log):
        """Test listing tool logs."""
        create_tool_log(tool_name="search")
        create_tool_log(tool_name="query")
        
        # Correct URL from router: /api/rag/tool-logs/
        response = api_client.get('/api/rag/tool-logs/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data or isinstance(data, list)
