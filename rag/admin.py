from django.contrib import admin
from rag.models import Document, ChatHistory, ToolLog


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at')
    search_fields = ('title', 'content')
    list_filter = ('created_at',)
    readonly_fields = ('id', 'created_at')


@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')
    list_filter = ('created_at',)
    readonly_fields = ('id', 'created_at')


@admin.register(ToolLog)
class ToolLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'tool_name', 'created_at')
    list_filter = ('tool_name', 'created_at')
    readonly_fields = ('id', 'created_at')
    search_fields = ('tool_name',)
