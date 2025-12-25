# Implementation Ideas & Roadmap for Agentic RAG

> **Strategic Guide for Completing the Agentic RAG System**

## 📋 Table of Contents
1. [Current State Analysis](#current-state-analysis)
2. [Web Search Integration](#web-search-integration)
3. [Knowledge Base Enhancements](#knowledge-base-enhancements)
4. [Frontend Implementation Plan](#frontend-implementation-plan)
5. [Deployment & Scaling](#deployment--scaling)

---

## 🔍 Current State Analysis

### ✅ What's Working
- **Core RAG Pipeline**: Router → Retrieval → Generation flow is functional
- **Vector Search**: Qdrant integration with embedding service
- **Document Ingestion**: PDF upload and chunking works
- **Memory System**: Three-tier architecture (short/medium/long-term)
- **WebSocket Chat**: Real-time communication infrastructure
- **Docker Setup**: Multi-container orchestration ready

### ⚠️ What Needs Implementation
- **Web Search**: Currently a placeholder, needs real implementation
- **Frontend**: No UI exists yet
- **Manual KB Creation**: API exists but needs better UI/UX
- **Advanced Features**: Analytics, search filters, bulk operations

---

## 🌐 Web Search Integration

### Option 1: Serper API (Recommended)
**Pros**: Google search results, reliable, affordable
**Implementation**:

```python
# apps/core/tools/serper.py
import os
import requests
from decouple import config

class SerperDevTool:
    """
    Google Search via Serper.dev API
    """
    
    def __init__(self):
        self.api_key = config("SERPER_API_KEY", default=None)
        self.base_url = "https://google.serper.dev/search"
    
    def search(self, query: str, num_results: int = 5):
        """
        Perform web search via Serper API
        
        Args:
            query: Search query string
            num_results: Number of results to return
            
        Returns:
            dict: Search results with organic results, snippets
        """
        if not self.api_key:
            return self._placeholder_response()
        
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "q": query,
            "num": num_results
        }
        
        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Serper search error: {e}")
            return self._placeholder_response()
    
    def _placeholder_response(self):
        return {
            "organic": [
                {
                    "title": "Web search unavailable",
                    "snippet": "Configure SERPER_API_KEY to enable web search",
                    "link": "#"
                }
            ]
        }
```

**Steps to Implement**:
1. Sign up at https://serper.dev (free tier: 2,500 queries/month)
2. Add `SERPER_API_KEY` to `.env`
3. Update `apps/core/agent/pipeline.py` to use `SerperDevTool`
4. Add requirements: `requests>=2.31.0` (already present)

**Estimated Time**: 2-3 hours

---

### Option 2: DuckDuckGo Search (Free Alternative)

```python
# Install: pip install duckduckgo-search

from duckduckgo_search import DDGS

class DuckDuckGoTool:
    def search(self, query: str, max_results: int = 5):
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            return {
                "organic": [
                    {
                        "title": r["title"],
                        "snippet": r["body"],
                        "link": r["href"]
                    }
                    for r in results
                ]
            }
```

**Pros**: Free, no API key required
**Cons**: Rate limiting, less reliable than Serper

**Add to `requirements.txt`**: `duckduckgo-search>=4.0.0`

---

### Option 3: Tavily API (AI-Optimized)

**Best for**: AI applications, returns structured data

```python
from tavily import TavilyClient

class TavilySearchTool:
    def __init__(self):
        self.client = TavilyClient(api_key=config("TAVILY_API_KEY"))
    
    def search(self, query: str):
        results = self.client.search(query, max_results=5)
        return {
            "organic": [
                {
                    "title": r["title"],
                    "snippet": r["content"],
                    "link": r["url"],
                    "score": r.get("score", 0)
                }
                for r in results.get("results", [])
            ]
        }
```

**Get API Key**: https://tavily.com (free tier available)

---

### Web Content Extraction (For All Options)

Add URL content fetching for richer context:

```python
# apps/core/tools/web_scraper.py
import requests
from bs4 import BeautifulSoup
from readability import Document

class WebContentExtractor:
    """Extract main content from web pages"""
    
    def extract(self, url: str, max_length: int = 5000):
        """
        Extract readable content from URL
        
        Args:
            url: Web page URL
            max_length: Maximum content length
            
        Returns:
            str: Extracted text content
        """
        try:
            response = requests.get(
                url,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=10
            )
            response.raise_for_status()
            
            # Use readability for clean extraction
            doc = Document(response.text)
            soup = BeautifulSoup(doc.summary(), 'html.parser')
            text = soup.get_text(separator=' ', strip=True)
            
            return text[:max_length]
        except Exception as e:
            print(f"Failed to extract from {url}: {e}")
            return ""
```

**Dependencies**:
```
beautifulsoup4>=4.12.0
readability-lxml>=0.8.1
```

**Integration**: Add to pipeline for top 2-3 search results

---

## 📚 Knowledge Base Enhancements

### 1. Manual Document Creation UI

**Backend** (Already exists): `POST /api/knowledgebase/documents/`

**Frontend Component Needed**:
```typescript
// ManualDocumentForm.tsx
const ManualDocumentForm = () => {
  const form = useForm({
    title: '',
    content: '',
    metadata: {
      category: '',
      tags: [],
      source: ''
    }
  });

  return (
    <form onSubmit={form.handleSubmit}>
      <Input label="Title" {...form.register('title')} required />
      <Textarea 
        label="Content" 
        {...form.register('content')} 
        rows={15}
        placeholder="Enter your knowledge base content here..."
      />
      <Input label="Category" {...form.register('metadata.category')} />
      <TagInput label="Tags" {...form.register('metadata.tags')} />
      <Button type="submit">Create Document</Button>
    </form>
  );
};
```

**Features to Add**:
- Rich text editor (TipTap or SlateJS)
- Markdown preview
- Auto-save drafts (localStorage)
- Template system for common document types

---

### 2. Bulk Document Operations

**Backend Enhancement**:

```python
# apps/knowledgebase/views.py

class DocumentViewSet(viewsets.ModelViewSet):
    # ... existing code ...
    
    @action(detail=False, methods=['post'])
    def bulk_upload(self, request):
        """Upload multiple PDFs at once"""
        files = request.FILES.getlist('files')
        results = []
        
        for file in files:
            try:
                doc = self.service.process_pdf(
                    file,
                    title=file.name,
                    metadata=request.data.get('metadata', {})
                )
                results.append({
                    'id': str(doc.id),
                    'title': doc.title,
                    'status': 'success'
                })
            except Exception as e:
                results.append({
                    'filename': file.name,
                    'status': 'error',
                    'error': str(e)
                })
        
        return Response({
            'total': len(files),
            'success': len([r for r in results if r['status'] == 'success']),
            'results': results
        })
    
    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        """Delete multiple documents"""
        doc_ids = request.data.get('ids', [])
        deleted = []
        
        for doc_id in doc_ids:
            try:
                self.service.delete_document(doc_id)
                deleted.append(doc_id)
            except Exception as e:
                print(f"Failed to delete {doc_id}: {e}")
        
        return Response({
            'deleted': deleted,
            'count': len(deleted)
        })
```

---

### 3. Document Collections/Namespaces

**New Model**:

```python
# apps/knowledgebase/models.py

class Collection(models.Model):
    """Group documents into collections"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'collections'
        ordering = ['name']

class Document(models.Model):
    # ... existing fields ...
    collection = models.ForeignKey(
        Collection,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents'
    )
```

**Benefits**:
- Organize documents by project/topic
- Scope searches to specific collections
- Better access control (future)

**Migration**: `python manage.py makemigrations && python manage.py migrate`

---

### 4. Additional File Format Support

```python
# apps/knowledgebase/services.py

class DocumentService:
    # ... existing code ...
    
    def process_docx(self, file_obj, title, metadata=None):
        """Process Word documents"""
        import docx
        doc = docx.Document(file_obj)
        text = '\n'.join([para.text for para in doc.paragraphs])
        return self._process_text(text, title, metadata)
    
    def process_txt(self, file_obj, title, metadata=None):
        """Process plain text files"""
        text = file_obj.read().decode('utf-8')
        return self._process_text(text, title, metadata)
    
    def process_markdown(self, file_obj, title, metadata=None):
        """Process Markdown files"""
        import markdown
        from bs4 import BeautifulSoup
        
        md_text = file_obj.read().decode('utf-8')
        html = markdown.markdown(md_text)
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        
        return self._process_text(text, title, metadata)
    
    def _process_text(self, text, title, metadata):
        """Common processing for all text-based formats"""
        # Chunking, embedding, storage (extracted from process_pdf)
        document = Document.objects.create(
            title=title,
            content=text,
            metadata=metadata or {}
        )
        
        # ... continue with chunking and embedding ...
        return document
```

**Dependencies to add**:
```
python-docx>=1.0.0
markdown>=3.5.0
```

---

### 5. Advanced Search & Filters

**Backend API Enhancement**:

```python
# apps/knowledgebase/views.py

class DocumentViewSet(viewsets.ModelViewSet):
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Advanced search with filters
        Query params:
          - q: search query
          - category: filter by category
          - tags: comma-separated tags
          - date_from, date_to: date range
          - collection_id: filter by collection
        """
        query = request.GET.get('q', '')
        category = request.GET.get('category')
        tags = request.GET.getlist('tags')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        collection_id = request.GET.get('collection_id')
        
        # Start with all documents
        queryset = Document.objects.all()
        
        # Apply filters
        if category:
            queryset = queryset.filter(metadata__category=category)
        
        if tags:
            for tag in tags:
                queryset = queryset.filter(metadata__tags__contains=[tag])
        
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        if collection_id:
            queryset = queryset.filter(collection_id=collection_id)
        
        # Perform search if query provided
        if query:
            # Combine keyword and vector search
            keyword_results = Document.keyword_search(query)
            
            from apps.vectorstore.services import QdrantService
            qdrant = QdrantService()
            vector_results = qdrant.search(query, limit=20)
            
            # Merge results (deduplicate and rank)
            # ... implementation ...
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
```

---

## 💻 Frontend Implementation Plan

### Phase 1: Project Setup (Week 1)

**1.1 Initialize React + Vite Project**

```bash
# Create frontend directory
cd agentic_rag
npm create vite@latest frontend -- --template react-ts
cd frontend

# Install core dependencies
pnpm add \
  react-router-dom \
  @tanstack/react-query \
  zustand \
  axios \
  socket.io-client

# Install UI libraries
pnpm add \
  tailwindcss \
  @headlessui/react \
  lucide-react \
  react-markdown \
  react-hook-form \
  zod

# Install dev dependencies
pnpm add -D \
  @types/node \
  @typescript-eslint/eslint-plugin \
  @typescript-eslint/parser \
  prettier \
  eslint
```

**1.2 Setup shadcn/ui**

```bash
npx shadcn-ui@latest init
npx shadcn-ui@latest add button input textarea card dialog tabs
```

**1.3 Configure Environment**

```env
# .env.local
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

---

### Phase 2: Core Features (Weeks 2-3)

**Priority Order**:

1. **Authentication & Layout** (if needed)
   - Login/Register (optional for MVP)
   - App shell with sidebar
   - Navigation

2. **Chat Interface** (MUST HAVE)
   - WebSocket connection
   - Message list with bubbles
   - Input with send button
   - Typing indicator
   - Source citations

3. **Knowledge Base Management** (MUST HAVE)
   - Document list view
   - PDF upload (drag-and-drop)
   - Manual document creation
   - Document viewer
   - Delete functionality

4. **Settings** (NICE TO HAVE)
   - Memory configuration
   - LLM provider selection
   - System preferences

---

### Phase 3: Advanced Features (Week 4)

1. **Analytics Dashboard**
   - Query statistics
   - Source breakdown charts
   - Document usage metrics

2. **Search & Filters**
   - Full-text search
   - Filter by category, tags, date
   - Sort options

3. **Bulk Operations**
   - Multi-select documents
   - Bulk delete
   - Bulk tag/categorize

---

### Simplified MVP Approach (If Time-Constrained)

**Ultra-minimal frontend (2-3 days)**:

```tsx
// App.tsx - Single-page application
import { useState } from 'react';
import { ChatInterface } from './components/ChatInterface';
import { DocumentUpload } from './components/DocumentUpload';

function App() {
  const [activeTab, setActiveTab] = useState<'chat' | 'upload'>('chat');

  return (
    <div className="h-screen flex flex-col">
      <header className="bg-gray-800 text-white p-4">
        <h1>Agentic RAG</h1>
      </header>
      
      <nav className="bg-gray-100 p-2">
        <button onClick={() => setActiveTab('chat')}>Chat</button>
        <button onClick={() => setActiveTab('upload')}>Upload</button>
      </nav>
      
      <main className="flex-1 overflow-hidden">
        {activeTab === 'chat' ? <ChatInterface /> : <DocumentUpload />}
      </main>
    </div>
  );
}
```

This gives you a working UI quickly, then you can iterate.

---

## 🚀 Deployment & Scaling

### Local Development Stack

```yaml
# docker-compose.yml (add frontend service)
services:
  # ... existing services ...
  
  frontend:
    build: ./frontend
    container_name: agentic_rag_frontend
    ports:
      - "3000:80"
    environment:
      - VITE_API_URL=http://web:8000
      - VITE_WS_URL=ws://web:8000
    depends_on:
      - web
```

### Production Deployment Options

#### Option 1: Single Server (Simplest)
- Deploy on AWS EC2 / DigitalOcean Droplet
- Use Docker Compose
- Nginx as reverse proxy

#### Option 2: Kubernetes (Scalable)
- Backend: Multiple Django pods
- Frontend: CDN + S3
- Qdrant: StatefulSet
- PostgreSQL: Managed RDS

#### Option 3: Serverless (Cost-Effective)
- Backend: AWS Lambda + API Gateway
- Frontend: Vercel / Netlify
- Database: Neon / Supabase

---

## 🎯 Implementation Priority Matrix

### High Priority (Must Do)
1. ✅ **Web Search Integration** (Serper or DuckDuckGo)
2. ✅ **Basic React Frontend** (Chat + Upload)
3. ✅ **Manual Document Creation UI**

### Medium Priority (Should Do)
4. **Document Collections/Namespaces**
5. **Advanced Search & Filters**
6. **Analytics Dashboard**

### Low Priority (Nice to Have)
7. **Multi-format document support**
8. **Bulk operations**
9. **Export/Import features**

---

## 📊 Feature Completion Checklist

### Backend
- [x] RAG pipeline with routing
- [x] PDF document ingestion
- [x] Vector search (Qdrant)
- [x] Keyword search (PostgreSQL)
- [x] Memory system (3-tier)
- [x] WebSocket chat
- [ ] **Web search implementation** (Serper/DuckDuckGo)
- [ ] Web content extraction
- [ ] Document collections
- [ ] Advanced search API
- [ ] Bulk operations API

### Frontend
- [ ] Project setup (Vite + React + TypeScript)
- [ ] Chat interface with WebSocket
- [ ] Document upload (drag-and-drop)
- [ ] Manual document creation form
- [ ] Document list & viewer
- [ ] Memory configuration UI
- [ ] Analytics dashboard
- [ ] Search & filters
- [ ] Responsive design
- [ ] Dark mode

### DevOps
- [x] Docker containerization
- [x] Docker Compose orchestration
- [x] Health checks
- [x] CI/CD pipeline (GitHub Actions)
- [ ] Production deployment guide
- [ ] Monitoring & logging
- [ ] Backup strategy

---

## 💡 Quick Wins (Do These First!)

### 1. Implement Serper Web Search (2-3 hours)
```bash
# Get API key from serper.dev
# Add to .env: SERPER_API_KEY=xxx
# Implement SerperDevTool class
# Update pipeline.py to use it
# Test with queries
```

### 2. Create Basic React Frontend (1 day)
```bash
# Initialize Vite project
# Add simple chat interface
# Add document upload
# Connect to WebSocket
# Test end-to-end flow
```

### 3. Add Manual Document Creation (2 hours)
```bash
# Add form in React
# Connect to POST /api/knowledgebase/documents/
# Add success/error handling
```

---

## 🎓 Learning Resources

### For Web Search
- Serper API docs: https://serper.dev/docs
- DuckDuckGo Search: https://github.com/deedy5/duckduckgo_search
- Web scraping: https://github.com/buriy/python-readability

### For React Frontend
- React docs: https://react.dev
- Vite: https://vitejs.dev
- shadcn/ui: https://ui.shadcn.com
- React Query: https://tanstack.com/query
- Zustand: https://github.com/pmndrs/zustand

---

## 🤔 Architecture Decisions

### Why Serper over alternatives?
- **Reliability**: Uses Google's search index
- **Cost**: 2,500 free queries/month
- **Quality**: Better results than free alternatives
- **Speed**: Fast response times

### Why Vite over Create React App?
- **Faster**: Lightning-fast HMR
- **Modern**: Better DX, native ESM
- **Smaller**: Optimized builds

### Why Zustand over Redux?
- **Simpler**: Less boilerplate
- **Lighter**: Smaller bundle size
- **Flexible**: Works great with React Query

---

## 📅 Suggested Timeline

### Week 1: Web Search + Backend Polish
- Implement Serper API integration
- Add web content extraction
- Test routing with real web results
- Fix any bugs in existing features

### Week 2: Frontend Foundation
- Setup React project
- Build chat interface
- Implement WebSocket connection
- Add document upload

### Week 3: Knowledge Base UI
- Document list view
- Manual document creation
- Document viewer
- Delete/update operations

### Week 4: Polish & Deploy
- Advanced features (analytics, filters)
- Responsive design
- Dark mode
- Production deployment

---

**Ready to build! Start with the quick wins and iterate from there. 🚀**
