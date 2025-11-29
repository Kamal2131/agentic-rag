# Agentic RAG System

A production-ready **Agentic RAG (Retrieval Augmented Generation with Agents)** system built with Django REST Framework. The system implements a ReAct-style agent that can analyze queries, plan actions, execute tools, and produce contextual answers.

## 🌟 Features

- **ReAct-Style Agent**: Intelligent agent with reasoning and action loop
- **Qdrant Vector Database**: High-performance vector search with dedicated Qdrant instance
- **Semantic Search**: Vector similarity search using OpenAI embeddings
- **Multiple Tools**:
  - Vector similarity search (Qdrant)
  - Keyword search (PostgreSQL trigram)
  - Safe SQL query execution
  - Web search (placeholder)
- **LLM Support**: Both OpenAI and Groq
- **Clean Architecture**: Services, tools, and agent executor pattern
- **REST API**: Complete DRF API with Swagger documentation
- **Docker Ready**: One-command deployment with Docker Compose

## 🚀 Quick Start with Docker

### Prerequisites

- Docker and Docker Compose installed
- OpenAI API key (or Groq API key)

### Setup

1. **Clone/Navigate to the project directory**

2. **Create environment file**:
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` and add your API keys**:
   ```bash
   OPENAI_API_KEY=your-openai-api-key-here
   GROQ_API_KEY=your-groq-api-key-here  # Optional
   ```

4. **Start the services**:
   ```bash
   docker-compose up --build
   ```

   This will start:
   - **PostgreSQL** (port 5432) - for data storage
   - **Qdrant** (ports 6333, 6334) - for vector search
   - **Django** (port 8000) - API server

5. **Access the application**:
   - API: http://localhost:8000
   - Admin: http://localhost:8000/admin
   - API Docs: http://localhost:8000/api/docs/
   - Qdrant Dashboard: http://localhost:6333/dashboard

### Create Admin User

```bash
docker-compose exec web python manage.py createsuperuser
```

## 📚 API Endpoints

### Document Upload
```bash
POST /api/rag/upload/
Content-Type: application/json

{
  "title": "Machine Learning Basics",
  "content": "Machine learning is a subset of AI...",
  "metadata": {"category": "AI", "tags": ["ML", "AI"]}
}
```

### Agentic RAG Query
```bash
POST /api/rag/query/
Content-Type: application/json

{
  "query": "What is machine learning?",
  "user": "john_doe"
}
```

**Response**:
```json
{
  "answer": "Based on the retrieved documents, machine learning is...",
  "sources": [
    {
      "id": "uuid",
      "title": "Machine Learning Basics",
      "content": "..."
    }
  ],
  "steps_taken": [
    {
      "step": 1,
      "thought": "I should search for documents about machine learning",
      "tool": "vector_search",
      "tool_input": {"query": "machine learning", "top_k": 5},
      "result": {...}
    }
  ]
}
```

### Other Endpoints

- **GET** `/api/rag/documents/` - List all documents
- **GET** `/api/rag/chat-history/` - Get chat history
- **GET** `/api/rag/tools/` - List available agent tools
- **GET** `/api/rag/tool-logs/` - View tool execution logs
- **GET** `/api/schema/` - OpenAPI schema
- **GET** `/api/docs/` - Interactive API documentation

## 🏗️ Architecture

```
agentic_rag/
├── config/              # Django configuration
├── rag/                 # Main RAG application
│   ├── models.py        # Database models (Document, ChatHistory, ToolLog)
│   ├── services/        # Business logic layer
│   │   ├── embedding_service.py    # OpenAI/Groq embeddings
│   │   ├── qdrant_service.py       # Qdrant vector operations
│   │   ├── vector_search_service.py # Vector similarity search
│   │   └── document_service.py      # Document CRUD
│   ├── tools/           # Agent tools
│   │   ├── vector_search_tool.py
│   │   ├── keyword_search_tool.py
│   │   ├── sql_query_tool.py
│   │   ├── web_search_tool.py
│   │   └── registry.py
│   ├── agent/           # Agent executor
│   │   ├── executor.py   # ReAct loop
│   │   ├── llm_client.py # LLM interface
│   │   └── prompts.py
│   ├── serializers/     # DRF serializers
│   ├── views.py         # API views
│   └── urls.py          # URL routing
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

### System Components

1. **PostgreSQL**: Stores document metadata and chat history
2. **Qdrant**: Dedicated vector database for embeddings and similarity search
3. **Django REST Framework**: API layer and business logic
4. **Agent Executor**: ReAct-style reasoning loop
5. **Tool Registry**: Pluggable tool system

## 🔧 Manual Setup (Without Docker)

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Qdrant (can run via Docker: `docker run -p 6333:6333 qdrant/qdrant`)

### Installation

1. **Start Qdrant** (if not using Docker Compose):
   ```bash
   docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings:
   # - OPENAI_API_KEY
   # - QDRANT_HOST=localhost (if running locally)
   # - Database credentials
   ```

5. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Start server**:
   ```bash
   python manage.py runserver
   ```

## 🛠️ Configuration

Edit `.env` file:

- `OPENAI_API_KEY`: Your OpenAI API key
- `GROQ_API_KEY`: Your Groq API key (optional)
- `DEFAULT_LLM_PROVIDER`: `openai` or `groq`
- `DEFAULT_EMBEDDING_PROVIDER`: `openai` or `groq`
- `AGENT_MODEL`: LLM model to use (default: `gpt-4-turbo-preview`)
- `MAX_AGENT_STEPS`: Maximum reasoning steps (default: 5)

## 🧪 Testing the System

### 1. Upload Documents

```bash
curl -X POST http://localhost:8000/api/rag/upload/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Programming",
    "content": "Python is a high-level programming language known for its simplicity..."
  }'
```

### 2. Query the Agent

```bash
curl -X POST http://localhost:8000/api/rag/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Python programming?"
  }'
```

### 3. View Tools

```bash
curl http://localhost:8000/api/rag/tools/
```

## 📊 Agent Workflow

1. **User sends query** → API receives request
2. **Agent Executor**:
   - Analyzes query
   - Plans which tools to use
   - Executes tools (vector search, keyword search, SQL)
   - Collects observations
   - Re-plans if needed
   - Generates final answer
3. **Response** → Returns answer with sources and execution steps

## 🛡️ Security Features

- Read-only SQL query tool (SELECT only)
- Dangerous SQL keyword blocking
- API request validation
- Environment-based configuration

## 🐳 Docker Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild
docker-compose up --build

# Access Django shell
docker-compose exec web python manage.py shell

# Run migrations
docker-compose exec web python manage.py migrate
```

## 📝 Development

### Adding New Tools

1. Create tool in `rag/tools/my_tool.py`
2. Register in `rag/tools/registry.py`
3. Tool will be automatically available to agent

### Extending the Agent

Modify `rag/agent/executor.py` to customize:
- Maximum steps
- Planning logic
- Observation handling
- Response formatting

## 🤝 Contributing

This is a complete, production-ready Agentic RAG system with:
- ✅ Clean architecture
- ✅ Modular design
- ✅ Comprehensive API
- ✅ Docker deployment
- ✅ LLM flexibility (OpenAI/Groq)
- ✅ Vector search with pgvector
- ✅ Agent tool execution
- ✅ Full documentation

## 📄 License

This project is provided as-is for educational and production use.

## 🆘 Troubleshooting

### Database Connection Error
- Ensure PostgreSQL is running
- Check environment variables in `.env`
- Verify pgvector extension is installed

### LLM API Errors
- Verify API keys in `.env`
- Check rate limits
- Ensure model names are correct

### Docker Issues
- Run `docker-compose down -v` to reset
- Check Docker logs: `docker-compose logs`
- Ensure ports 8000 and 5432 are available

## 📞 Support

For issues or questions:
1. Check API documentation at `/api/docs/`
2. Review tool logs at `/api/rag/tool-logs/`
3. Check agent execution steps in query responses
