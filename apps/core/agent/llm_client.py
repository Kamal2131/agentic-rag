"""
LLM Client for agent planning and reasoning.
"""

from django.conf import settings
from groq import Groq
from openai import OpenAI


class LLMClient:
    """
    Client for interacting with LLMs (OpenAI or Groq).
    """

    def __init__(self, provider=None):
        """
        Initialize the LLM client.

        Args:
            provider: 'openai' or 'groq'. If None, uses DEFAULT_PROVIDER from settings
        """
        self.provider = provider or settings.LLM_CONFIG["DEFAULT_PROVIDER"]
        self.model = settings.LLM_CONFIG["AGENT_MODEL"]

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
            # Use Groq-compatible model if needed
            if "gpt" in self.model:
                self.model = "llama-3.1-70b-versatile"
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def chat(self, messages, temperature=0.7, json_mode=False):
        """
        Send chat messages to LLM.

        Args:
            messages (list): List of message dicts
            temperature (float): Sampling temperature
            json_mode (bool): Whether to enforce JSON output

        Returns:
            str: LLM response content
        """
        try:
            kwargs = {"model": self.model, "messages": messages, "temperature": temperature}

            if json_mode and self.provider == "openai":
                kwargs["response_format"] = {"type": "json_object"}

            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"LLM chat failed: {str(e)}")
