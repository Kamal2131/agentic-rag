"""
ViewSets for RAG API endpoints.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter

from apps.rag.models import Document, ChatHistory, ToolLog
from apps.rag.serializers.serializers import (
    DocumentSerializer, DocumentUploadSerializer, QuerySerializer,
    QueryResponseSerializer, ChatHistorySerializer, ToolLogSerializer,
    ToolMetadataSerializer
)
from apps.rag.services.document_service import DocumentService
from apps.rag.agent.executor import AgentExecutor
from apps.rag.tools.registry import ToolRegistry


class DocumentViewSet(viewsets.ViewSet):
    """
    ViewSet for document operations.
    """
    
    @extend_schema(
        request=DocumentUploadSerializer,
        responses={201: DocumentSerializer}
    )
    @action(detail=False, methods=['post'], url_path='upload')
    def upload(self, request):
        """
        Upload and embed a document.
        """
        serializer = DocumentUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            document_service = DocumentService()
            document = document_service.create_document(
                title=serializer.validated_data['title'],
                content=serializer.validated_data['content'],
                metadata=serializer.validated_data.get('metadata', {})
            )
            
            response_serializer = DocumentSerializer(document)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(responses={200: DocumentSerializer(many=True)})
    def list(self, request):
        """
        List all documents.
        """
        documents = Document.objects.all()[:100]
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)
    
    @extend_schema(responses={200: DocumentSerializer})
    def retrieve(self, request, pk=None):
        """
        Retrieve a specific document.
        """
        try:
            document = Document.objects.get(pk=pk)
            serializer = DocumentSerializer(document)
            return Response(serializer.data)
        except Document.DoesNotExist:
            return Response(
                {'error': 'Document not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class QueryViewSet(viewsets.ViewSet):
    """
    ViewSet for agentic RAG queries.
    """
    
    @extend_schema(
        request=QuerySerializer,
        responses={200: QueryResponseSerializer}
    )
    @action(detail=False, methods=['post'], url_path='query')
    def query(self, request):
        """
        Execute an agentic RAG query.
        """
        serializer = QuerySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        query_text = serializer.validated_data['query']
        user = serializer.validated_data.get('user', 'anonymous')
        
        try:
            # Execute agent
            executor = AgentExecutor()
            result = executor.run(query_text)
            
            # Save to chat history
            ChatHistory.objects.create(
                user=user,
                messages=[
                    {'role': 'user', 'content': query_text},
                    {'role': 'assistant', 'content': result['answer']}
                ]
            )
            
            response_serializer = QueryResponseSerializer(data=result)
            if response_serializer.is_valid():
                return Response(response_serializer.data)
            else:
                return Response(result)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChatHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for chat history.
    """
    queryset = ChatHistory.objects.all()
    serializer_class = ChatHistorySerializer
    
    @extend_schema(
        parameters=[
            OpenApiParameter('user', str, description='Filter by user')
        ]
    )
    def list(self, request):
        """
        List chat history, optionally filtered by user.
        """
        queryset = self.queryset
        user = request.query_params.get('user')
        if user:
            queryset = queryset.filter(user=user)
        
        queryset = queryset[:50]  # Limit to 50 recent
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class ToolsViewSet(viewsets.ViewSet):
    """
    ViewSet for listing available tools.
    """
    
    @extend_schema(responses={200: ToolMetadataSerializer(many=True)})
    def list(self, request):
        """
        List all available agent tools.
        """
        registry = ToolRegistry()
        tool_descriptions = registry.get_tool_descriptions()
        
        tools = []
        for name, metadata in tool_descriptions.items():
            tools.append(metadata)
        
        serializer = ToolMetadataSerializer(tools, many=True)
        return Response(serializer.data)


class ToolLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for tool execution logs.
    """
    queryset = ToolLog.objects.all()[:100]
    serializer_class = ToolLogSerializer

