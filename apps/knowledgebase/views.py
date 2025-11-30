"""
Views for Knowledge Base.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema

from apps.knowledgebase.models import Document
from apps.knowledgebase.serializers import DocumentSerializer, DocumentUploadSerializer
from apps.knowledgebase.services import DocumentService

class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing documents.
    """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    
    def get_serializer_class(self):
        if self.action == 'upload':
            return DocumentUploadSerializer
        return DocumentSerializer
    
    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'file': {'type': 'string', 'format': 'binary'},
                    'title': {'type': 'string'},
                    'metadata': {'type': 'object'}
                }
            }
        },
        responses={201: DocumentSerializer}
    )
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload(self, request):
        """
        Upload and process a PDF document.
        """
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        title = request.data.get('title', file_obj.name)
        
        try:
            service = DocumentService()
            document = service.process_pdf(file_obj, title)
            
            serializer = DocumentSerializer(document)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
