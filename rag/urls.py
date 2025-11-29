"""
URL configuration for RAG app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rag.views import (
    DocumentViewSet, QueryViewSet, ChatHistoryViewSet,
    ToolsViewSet, ToolLogViewSet
)

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'chat-history', ChatHistoryViewSet, basename='chat-history')
router.register(r'tools', ToolsViewSet, basename='tools')
router.register(r'tool-logs', ToolLogViewSet, basename='tool-logs')

urlpatterns = [
    # Document upload
    path('upload/', DocumentViewSet.as_view({'post': 'upload'}), name='upload'),
    
    # Agentic RAG query
    path('query/', QueryViewSet.as_view({'post': 'query'}), name='query'),
    
    # Router URLs
    path('', include(router.urls)),
]
