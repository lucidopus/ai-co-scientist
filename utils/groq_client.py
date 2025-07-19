from groq import Groq
from typing import Dict, Any, Optional
import logging

from utils.config import GROQ_API_KEY, PRIMARY_MODEL, SECONDARY_MODEL

logger = logging.getLogger(__name__)

class GroqClient:
    """Client for interacting with GROQ API"""
    
    def __init__(self):
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=GROQ_API_KEY)
        self.primary_model = PRIMARY_MODEL
        self.secondary_model = SECONDARY_MODEL
    
    def chat_completion(
        self,
        messages: list[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate chat completion using GROQ API
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use (defaults to primary model)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional arguments for the API
        
        Returns:
            Generated text response
        """
        try:
            if model is None:
                model = self.primary_model
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error in GROQ chat completion: {e}")
            raise
    
    def generate_with_system_prompt(
        self,
        system_prompt: str,
        user_message: str,
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate response with system prompt and user message
        
        Args:
            system_prompt: System prompt to set context
            user_message: User message
            model: Model to use
            **kwargs: Additional arguments
        
        Returns:
            Generated response
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        return self.chat_completion(messages, model=model, **kwargs)

# Global client instance
groq_client = GroqClient()