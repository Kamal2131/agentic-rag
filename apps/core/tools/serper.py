"""
Serper.dev Tool for web search.
"""

import json

import requests
from django.conf import settings


class SerperDevTool:
    """
    Tool for searching the web using Serper.dev API.
    """

    def __init__(self):
        self.api_key = settings.SERPER_API_KEY
        self.url = "https://google.serper.dev/search"

    def search(self, query):
        """
        Execute web search.

        Args:
            query (str): Search query

        Returns:
            dict: Search results
        """
        payload = json.dumps({"q": query})
        headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}

        try:
            response = requests.request("POST", self.url, headers=headers, data=payload)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
