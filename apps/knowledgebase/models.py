import uuid

from django.contrib.postgres.search import TrigramSimilarity
from django.db import models


class Document(models.Model):
    """
    Document model for RAG.
    Vector embeddings are stored in Qdrant.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=500)
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "documents"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["title"]),
        ]

    def __str__(self):
        return self.title

    @classmethod
    def keyword_search(cls, query, top_k=10):
        """
        Perform keyword-based search using PostgreSQL trigram similarity.

        Args:
            query: Search query string
            top_k: Number of results to return

        Returns:
            QuerySet of Documents ordered by relevance
        """
        return (
            cls.objects.annotate(
                similarity=TrigramSimilarity("content", query) + TrigramSimilarity("title", query)
            )
            .filter(similarity__gt=0.1)
            .order_by("-similarity")[:top_k]
        )
