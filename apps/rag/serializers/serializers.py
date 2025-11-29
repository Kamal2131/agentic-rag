"""
Serializers for RAG models and API requests/responses.
"""

from rest_framework import serializers
from apps.rag.models import Document, ChatHistory, ToolLog


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for Document model."""
    
    class Meta:
        model = Document
        fields = ['id', 'title', 'content', 'metadata', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class DocumentUploadSerializer(serializers.Serializer):
    """Serializer for document upload requests."""
    
    title = serializers.CharField(max_length=500)
    content = serializers.CharField()
    metadata = serializers.JSONField(required=False, default=dict)


class QuerySerializer(serializers.Serializer):
    """Serializer for query requests."""
    
    query = serializers.CharField()
    user = serializers.CharField(required=False, allow_blank=True)


class QueryResponseSerializer(serializers.Serializer):
    """Serializer for query responses."""
    
    answer = serializers.CharField()
    sources = serializers.ListField(child=serializers.DictField())
    steps_taken = serializers.ListField(child=serializers.DictField())


class ChatHistorySerializer(serializers.ModelSerializer):
    """Serializer for ChatHistory model."""
    
    class Meta:
        model = ChatHistory
        fields = ['id', 'user', 'messages', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ToolLogSerializer(serializers.ModelSerializer):
    """Serializer for ToolLog model."""
    
    class Meta:
        model = ToolLog
        fields = ['id', 'tool_name', 'input_data', 'output_data', 'created_at']
        read_only_fields = ['id', 'created_at']


class ToolMetadataSerializer(serializers.Serializer):
    """Serializer for tool metadata."""
    
    name = serializers.CharField()
    description = serializers.CharField()
    parameters = serializers.DictField()
