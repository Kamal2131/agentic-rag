# API Reference Guide

> **Complete API Documentation for Agentic RAG Backend**

## Base URL
```
Development: http://localhost:8000
Production: https://your-domain.com
```

---

## 📚 Knowledge Base API

### Upload Document (PDF)
**Endpoint**: `POST /api/knowledgebase/documents/upload/`  
**Content-Type**: `multipart/form-data`

**Request Body**:
```javascript
{
  "file": File,              // PDF file (required)
  "title": "string",         // Document title (optional, defaults to filename)
  "metadata": {              // Optional metadata object
    "category": "string",
    "tags": ["tag1", "tag2"],
    "source": "string"
  }
}
```

**Response** (`201 Created`):
```json
{
  "id": "uuid",
  "title": "Document Title",
  "content": "Extracted text content...",
  "metadata": {
    "category": "research",
    "tags": ["ai", "ml"]
  },
  "created_at": "2024-12-03T10:00:00Z",
  "updated_at": "2024-12-03T10:00:00Z"
}
```

**Example (curl)**:
```bash
curl -X POST http://localhost:8000/api/knowledgebase/documents/upload/ \
  -F "file=@document.pdf" \
  -F "title=My Research Paper" \
  -F 'metadata={"category":"research","tags":["ai"]}'
```

**Example (JavaScript)**:
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('title', 'My Document');
formData.append('metadata', JSON.stringify({ category: 'research' }));

const response = await fetch('/api/knowledgebase/documents/upload/', {
  method: 'POST',
  body: formData
});
const document = await response.json();
```

---

### Create Document Manually
**Endpoint**: `POST /api/knowledgebase/documents/`  
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "title": "string",                    // Required
  "content": "string",                  // Required
  "metadata": {                         // Optional
    "category": "string",
    "tags": ["string"],
    "source": "string"
  }
}
```

**Response** (`201 Created`):
```json
{
  "id": "uuid",
  "title": "Document Title",
  "content": "Document content...",
  "metadata": {},
  "created_at": "2024-12-03T10:00:00Z",
  "updated_at": "2024-12-03T10:00:00Z"
}
```

**Example (Python)**:
```python
import requests

response = requests.post(
    'http://localhost:8000/api/knowledgebase/documents/',
    json={
        'title': 'Company Policy',
        'content': 'Our company values...',
        'metadata': {
            'category': 'policy',
            'tags': ['hr', 'internal']
        }
    }
)
document = response.json()
```

---

### List Documents
**Endpoint**: `GET /api/knowledgebase/documents/`

**Query Parameters**:
- `limit`: Number of documents to return (default: 100)
- `offset`: Pagination offset (default: 0)

**Response** (`200 OK`):
```json
{
  "count": 42,
  "next": "/api/knowledgebase/documents/?offset=100",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "title": "Document 1",
      "content": "...",
      "metadata": {},
      "created_at": "2024-12-03T10:00:00Z",
      "updated_at": "2024-12-03T10:00:00Z"
    }
  ]
}
```

---

### Retrieve Document
**Endpoint**: `GET /api/knowledgebase/documents/{id}/`

**Response** (`200 OK`):
```json
{ 
  "id": "uuid",
  "title": "Document Title",
  "content": "Full document content...",
  "metadata": {},
  "created_at": "2024-12-03T10:00:00Z",
  "updated_at": "2024-12-03T10:00:00Z"
}
```

---

### Update Document
**Endpoint**: `PUT /api/knowledgebase/documents/{id}/`  
**Content-Type**: `application/json`

**Request Body** (all fields optional):
```json
{
  "title": "Updated Title",
  "content": "Updated content",
  "metadata": {
    "category": "new-category"
  }
}
```

**Response** (`200 OK`): Updated document object

---

### Delete Document
**Endpoint**: `DELETE /api/knowledgebase/documents/{id}/`

**Response** (`204 No Content`)

**Note**: This will also delete the document's vector embeddings from Qdrant.

---

## 💬 Chat & RAG API

### Execute RAG Query
**Endpoint**: `POST /api/rag/query/`  
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "query": "string",                    // Required: User question
  "conversation_id": "string",          // Optional: For conversation continuity
  "use_memory": true,                   // Optional: Include memory context (default: true)
  "source_hint": "local|web|both"       // Optional: Override router decision
}
```

**Response** (`200 OK`):
```json
{
  "answer": "The answer to your question...",
  "source": "both",
  "sources": [
    {
      "type": "local",
      "title": "Document Title",
      "content": "Relevant excerpt...",
      "score": 0.95
    },
    {
      "type": "web",
      "title": "Web Page",
      "url": "https://example.com",
      "content": "Web excerpt...",
      "score": 0.87
    }
  ],
  "steps": [
    {"step": "routing", "result": "both"},
    {"step": "retrieval_local", "count": 3},
    {"step": "retrieval_web", "count": 5},
    {"step": "context_building", "length": 2847},
    {"step": "generation", "tokens": 312}
  ],
  "metadata": {
    "response_time_ms": 1247,
    "llm_provider": "openai",
    "model": "gpt-4"
  }
}
```

**Example (JavaScript)**:
```javascript
const response = await fetch('/api/rag/query/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'What are the key features of RAG?',
    conversation_id: 'conv-123',
    use_memory: true
  })
});
const result = await response.json();
console.log(result.answer);
```

---

### Vector Search
**Endpoint**: `POST /api/rag/search/`  
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "query": "string",         // Required: Search query
  "limit": 10,               // Optional: Number of results (default: 10)
  "threshold": 0.7           // Optional: Similarity threshold (default: 0.7)
}
```

**Response** (`200 OK`):
```json
{
  "results": [
    {
      "id": "uuid",
      "content": "Relevant text chunk...",
      "score": 0.95,
      "metadata": {
        "document_id": "uuid",
        "title": "Source Document",
        "chunk_index": 3
      }
    }
  ],
  "count": 10
}
```

---

### Get Chat History
**Endpoint**: `GET /api/rag/history/`

**Query Parameters**:
- `user`: Filter by user (optional)
- `limit`: Number of chats (default: 50)

**Response** (`200 OK`):
```json
{
  "history": [
    {
      "id": 1,
      "user": "john_doe",
      "messages": [
        {
          "role": "user",
          "content": "Hello",
          "timestamp": "2024-12-03T10:00:00Z"
        },
        {
          "role": "assistant",
          "content": "Hi! How can I help?",
          "timestamp": "2024-12-03T10:00:01Z"
        }
      ],
      "created_at": "2024-12-03T10:00:00Z",
      "updated_at": "2024-12-03T10:05:00Z"
    }
  ]
}
```

---

## 🧠 Memory API

### Get Memory Configuration
**Endpoint**: `GET /api/memory/config/`

**Response** (`200 OK`):
```json
{
  "short_term_ttl": 3600,            // seconds
  "medium_term_ttl": 24,             // hours
  "long_term_enabled": true,
  "extraction_enabled": true
}
```

---

### Update Memory Configuration
**Endpoint**: `POST /api/memory/config/`  
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "short_term_ttl": 7200,            // Optional
  "medium_term_ttl": 48,             // Optional
  "long_term_enabled": true,         // Optional
  "extraction_enabled": true         // Optional
}
```

**Response** (`200 OK`): Updated configuration object

---

### Get Memory Statistics
**Endpoint**: `GET /api/memory/stats/`

**Response** (`200 OK`):
```json
{
  "short_term": {
    "active_sessions": 15,
    "total_messages": 342
  },
  "medium_term": {
    "active_sessions": 8,
    "total_summaries": 47
  },
  "long_term": {
    "total_entities": 123,
    "total_facts": 89,
    "total_preferences": 34
  }
}
```

---

## 🔌 WebSocket API

### Chat WebSocket
**Endpoint**: `ws://localhost:8000/ws/chat/`

**Connection Parameters**:
- `conversation_id` (optional): Resume existing conversation

**Message Format (Client → Server)**:
```json
{
  "type": "message",
  "content": "User message text"
}
```

**Message Format (Server → Client)**:
```json
{
  "type": "message",
  "role": "assistant",
  "content": "AI response text",
  "sources": [...],
  "timestamp": "2024-12-03T10:00:00Z"
}
```

**Typing Indicator (Server → Client)**:
```json
{
  "type": "typing",
  "is_typing": true
}
```

**Error Message (Server → Client)**:
```json
{
  "type": "error",
  "message": "Error description",
  "code": "ERROR_CODE"
}
```

**Example (JavaScript)**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat/?conversation_id=conv-123');

ws.onopen = () => {
  console.log('Connected');
  ws.send(JSON.stringify({
    type: 'message',
    content: 'Hello!'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'message') {
    console.log('AI:', data.content);
  }
};
```

**Example (Python with websockets)**:
```python
import asyncio
import websockets
import json

async def chat():
    uri = "ws://localhost:8000/ws/chat/"
    async with websockets.connect(uri) as websocket:
        # Send message
        await websocket.send(json.dumps({
            "type": "message",
            "content": "Hello!"
        }))
        
        # Receive response
        response = await websocket.recv()
        data = json.loads(response)
        print(f"AI: {data['content']}")

asyncio.run(chat())
```

---

## 🏥 Health & Status API

### Health Check
**Endpoint**: `GET /health/`

**Response** (`200 OK`):
```json
{
  "status": "healthy",
  "services": {
    "database": "up",
    "qdrant": "up",
    "redis": "up"
  },
  "timestamp": "2024-12-03T10:00:00Z"
}
```

---

## 🛡️ Error Responses

### Standard Error Format
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}                    // Optional additional details
  }
}
```

### Common Status Codes
- `200 OK`: Success
- `201 Created`: Resource created
- `204 No Content`: Success with no response body
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Example Error Responses

**400 Bad Request**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "title": ["This field is required."],
      "content": ["This field may not be blank."]
    }
  }
}
```

**404 Not Found**:
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Document not found",
    "details": {
      "document_id": "uuid-that-doesnt-exist"
    }
  }
}
```

---

## 📝 Request/Response Examples

### Complete Workflow: Upload → Query

**Step 1: Upload a Document**
```bash
curl -X POST http://localhost:8000/api/knowledgebase/documents/upload/ \
  -F "file=@machine-learning.pdf" \
  -F "title=ML Research Paper" \
  -F 'metadata={"category":"research","tags":["ml","ai"]}'
```

**Step 2: Wait for Processing** (automatic)
- Document is chunked
- Embeddings are generated
- Vectors stored in Qdrant

**Step 3: Query the Knowledge Base**
```bash
curl -X POST http://localhost:8000/api/rag/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the key concepts in machine learning?",
    "use_memory": true
  }'
```

**Step 4: Receive Answer with Sources**
```json
{
  "answer": "Machine learning key concepts include supervised learning, unsupervised learning, neural networks, and deep learning...",
  "source": "local",
  "sources": [
    {
      "type": "local",
      "title": "ML Research Paper",
      "content": "Machine learning is...",
      "score": 0.94
    }
  ]
}
```

---

## 🔐 Authentication (Future)

Currently, the API is open. For production, implement JWT authentication:

**Login** (Future):
```bash
POST /api/auth/login/
{
  "username": "user",
  "password": "pass"
}
→ Returns: {"token": "jwt-token"}
```

**Authenticated Requests**:
```bash
curl -H "Authorization: Bearer jwt-token" \
  http://localhost:8000/api/knowledgebase/documents/
```

---

## 📊 Rate Limiting (Future)

Planned rate limits:
- **Free tier**: 100 requests/hour
- **Pro tier**: 1000 requests/hour
- **Enterprise**: Unlimited

---

## 🧪 Testing the API

### Using Swagger UI
Navigate to: `http://localhost:8000/api/schema/swagger-ui/`
- Interactive API documentation
- Try out endpoints
- See request/response schemas

### Using Postman
Import collection from: `/docs/postman_collection.json` (to be created)

### Using cURL
See examples throughout this document

---

## 🎯 Best Practices

1. **Always handle errors**: Check status codes and error messages
2. **Use pagination**: Don't fetch all documents at once
3. **Validate inputs**: Use proper data types and formats
4. **Optimize queries**: Be specific to reduce processing time
5. **Monitor rate limits**: Implement exponential backoff
6. **Close WebSocket connections**: Prevent resource leaks

---

## 📚 Additional Resources

- **OpenAPI Spec**: `/api/schema/`
- **Swagger UI**: `/api/schema/swagger-ui/`
- **ReDoc**: `/api/schema/redoc/`
- **GitHub**: [Repository URL]
- **Documentation**: `/docs/`

---

**Questions? Open an issue on GitHub or contact support.**
