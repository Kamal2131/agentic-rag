import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestToolsAPI:
    """Test tools listing API."""

    def test_list_tools(self, api_client):
        """Test listing available tools."""
        # Use direct URL path instead of reverse
        response = api_client.get('/api/rag/tools/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        # Check tool structure
        tool = data[0]
        assert 'name' in tool
        assert 'description' in tool


@pytest.mark.django_db
class TestDocumentUploadAPI:
    """Test document upload API."""

    def test_upload_document(self, api_client, monkeypatch):
        """Test uploading a document."""
        # Mock embedding service to avoid API calls
        def mock_generate(self, text):
            return [0.1] * 1536
        
        from apps.rag.services import embedding_service
        monkeypatch.setattr(embedding_service.EmbeddingService, 'generate_embedding', mock_generate)
        
        # Use direct URL path
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
        
        # Use direct URL path
        response = api_client.get('/api/rag/history/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data
        assert len(data['results']) >= 2

    def test_retrieve_chat_history(self, api_client, create_chat_history):
        """Test retrieving specific chat history."""
        chat = create_chat_history()
        # Use direct URL path
        response = api_client.get(f'/api/rag/history/{chat.id}/')
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
        
        # Use direct URL path
        response = api_client.get('/api/rag/logs/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data
        assert len(data['results']) >= 2
