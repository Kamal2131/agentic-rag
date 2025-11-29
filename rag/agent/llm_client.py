"""
LLM Client for agent planning and reasoning.
"""

import json
from django.conf import settings
from openai import OpenAI
from groq import Groq


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
        self.provider = provider or settings.LLM_CONFIG['DEFAULT_PROVIDER']
        self.model = settings.LLM_CONFIG['AGENT_MODEL']
        
        if self.provider == 'openai':
            api_key = settings.LLM_CONFIG['OPENAI_API_KEY']
            if not api_key:
                raise ValueError("OpenAI API key not configured")
            self.client = OpenAI(api_key=api_key)
        elif self.provider == 'groq':
            api_key = settings.LLM_CONFIG['GROQ_API_KEY']
            if not api_key:
                raise ValueError("Groq API key not configured")
            self.client = Groq(api_key=api_key)
            # Use Groq-compatible model
            self.model = 'llama-3.1-70b-versatile'
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def plan(self, system_prompt, messages):
        """
        Generate a plan/action using the LLM.
        
        Args:
            system_prompt (str): System prompt with instructions
            messages (list): List of message dicts (role, content)
            
        Returns:
            dict: Parsed response with thought, tool, tool_input, final_answer
        """
        try:
            # Build messages
            chat_messages = [{'role': 'system', 'content': system_prompt}]
            chat_messages.extend(messages)
            
            # Call LLM
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=chat_messages,
                    temperature=0.7,
                    response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content
            elif self.provider == 'groq':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=chat_messages,
                    temperature=0.7
                )
                content = response.choices[0].message.content
            
            # Parse JSON response
            parsed = self._parse_response(content)
            return parsed
            
        except Exception as e:
            raise Exception(f"LLM planning failed: {str(e)}")
    
    def _parse_response(self, content):
        """
        Parse LLM response into structured format.
        
        Args:
            content (str): LLM response content
            
        Returns:
            dict: Parsed response
        """
        try:
            # Try to parse as JSON
            parsed = json.loads(content)
            
            # Validate required fields
            if 'thought' not in parsed:
                parsed['thought'] = ''
            if 'tool' not in parsed:
                parsed['tool'] = None
            if 'tool_input' not in parsed:
                parsed['tool_input'] = None
            if 'final_answer' not in parsed:
                parsed['final_answer'] = None
            
            return parsed
        except json.JSONDecodeError:
            # Fallback: try to extract JSON from the content
            try:
                # Look for JSON block
                start = content.find('{')
                end = content.rfind('}') + 1
                if start != -1 and end > start:
                    json_str = content[start:end]
                    return json.loads(json_str)
            except:
                pass
            
            # Return error format
            return {
                'thought': 'Failed to parse response',
                'tool': None,
                'tool_input': None,
                'final_answer': f'Error: Could not parse LLM response: {content}'
            }
