"""
Embedding Service for generating embeddings from text.
Supports OpenAI and Groq providers.
"""

from django.conf import settings
from groq import Groq
from openai import OpenAI


class EmbeddingService:
    """
    Service class for generating text embeddings.
    """

    def __init__(self, provider=None):
        """
        Initialize the embedding service.

        Args:
            provider: 'openai' or 'groq'. If None, uses DEFAULT_PROVIDER from settings
        """
        self.provider = provider or settings.EMBEDDING_CONFIG["DEFAULT_PROVIDER"]
        self.model = settings.EMBEDDING_CONFIG["EMBEDDING_MODEL"]
        self.dimension = settings.EMBEDDING_CONFIG["EMBEDDING_DIMENSION"]

        if self.provider == "openai":
            api_key = settings.LLM_CONFIG["OPENAI_API_KEY"]
            if not api_key:
                raise ValueError("OpenAI API key not configured")
            self.client = OpenAI(api_key=api_key)
        elif self.provider == "groq":
            api_key = settings.LLM_CONFIG["GROQ_API_KEY"]
            if not api_key:
                raise ValueError("Groq API key not configured")
            self.client = Groq(api_key=api_key)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def embed(self, text):
        """
        Generate embedding for the given text.

        Args:
            text: Input text to embed

        Returns:
            list[float]: Embedding vector
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        try:
            if self.provider == "openai":
                response = self.client.embeddings.create(model=self.model, input=text)
                return response.data[0].embedding
            elif self.provider == "groq":
                # Note: Groq may not support embeddings directly
                # This is a placeholder implementation
                raise NotImplementedError("Groq embedding not yet supported")
        except Exception as e:
            raise Exception(f"Failed to generate embedding: {str(e)}") from e

    def embed_batch(self, texts):
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of input texts

        Returns:
            list[list[float]]: List of embedding vectors
        """
        if not texts:
            return []

        try:
            if self.provider == "openai":
                response = self.client.embeddings.create(model=self.model, input=texts)
                return [item.embedding for item in response.data]
            elif self.provider == "groq":
                raise NotImplementedError("Groq embedding not yet supported")
        except Exception as e:
            raise Exception(f"Failed to generate embeddings: {str(e)}") from e
