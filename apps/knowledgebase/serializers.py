"""
Document serializer for RAG.
"""
from rest_framework import serializers
from .models import Document

class DocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for Document model.
    Exposes document details including metadata and timestamps.
    """
    class Meta:
        model = Document
        fields = ['id', 'title', 'content', 'metadata', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class DocumentUploadSerializer(serializers.Serializer):
    """
    Serializer for uploading new documents.
    Validates input before creating a Document instance.
    """
    title = serializers.CharField(max_length=500, required=True)
<<<<<<< HEAD
    content = serializers.CharField(required=False)
=======
    content = serializers.CharField(required=False) # Optional if file is provided, but here we use it for direct text or file handling logic in view
>>>>>>> a4e19396f3973d0407a4d44e657a0bf4900779a3
    metadata = serializers.JSONField(required=False, default=dict)
