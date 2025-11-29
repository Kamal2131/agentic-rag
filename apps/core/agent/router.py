"""
Router for RAG pipeline.
"""

import json
from apps.core.agent.llm_client import LLMClient

class Router:
    """
    Router to decide which data source to use.
    """
    
    def __init__(self):
        self.llm_client = LLMClient()
    
    def route(self, query, summary=None):
        """
        Route the query to appropriate source.
        
        Args:
            query (str): User query
            summary (str): Summary of local knowledge base (optional)
            
        Returns:
            str: 'local', 'web', or 'both'
        """
        system_prompt = """You are a router for a RAG system. 
        Your job is to decide where to look for information to answer the user's query.
        
        Available sources:
        1. "local": Use this if the query relates to the provided summary of the local document.
        2. "web": Use this if the query requires up-to-date information, news, or general knowledge not covered by the local document.
        3. "both": Use this if the query might need both local context and external information.
        
        Output JSON format: {"source": "local" | "web" | "both"}
        """
        
        user_content = f"Query: {query}\n"
        if summary:
            user_content += f"Local Document Summary: {summary}\n"
            
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        try:
            response = self.llm_client.chat(messages, json_mode=True)
            parsed = json.loads(response)
            return parsed.get("source", "web")
        except Exception:
            # Default to web if routing fails or parsing fails
            return "web"
