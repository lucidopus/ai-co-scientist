from typing import Dict, Any, Optional, List
import logging
from openai import OpenAI

from utils.groq_client import groq_client
from utils.helper import ask_gemma
from utils.config import OPENAI_API_KEY, PRIMARY_MODEL, SECONDARY_MODEL

logger = logging.getLogger(__name__)

class UnifiedLLMClient:
    """Unified client that can use GROQ, OpenAI, and Gemma models strategically"""
    
    def __init__(self):
        # Initialize OpenAI client if API key is available
        self.openai_client = None
        if OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Model capabilities and use cases
        self.model_strategies = {
            "complex_reasoning": "llama-3.3-70b-versatile",  # GROQ Llama for complex analysis
            "fast_operations": "gemma2-9b-it",              # GROQ Gemma for quick tasks
            "creative_generation": "gemma3:12b",            # Gemma 3 12B for creative tasks
            "precise_analysis": "o3-mini",                  # OpenAI o3-mini for precise analysis
        }
    
    def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model_strategy: str = "complex_reasoning",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate response using the best model for the given strategy
        
        Args:
            prompt: The input prompt
            system_prompt: Optional system prompt
            model_strategy: Strategy for model selection
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional arguments
        
        Returns:
            Generated response text
        """
        try:
            model = self.model_strategies.get(model_strategy, "complex_reasoning")
            
            if model == "o3-mini" and self.openai_client:
                return self._call_openai(prompt, system_prompt, temperature, max_tokens, **kwargs)
            elif model == "gemma3:12b":
                return self._call_gemma(prompt, system_prompt, **kwargs)
            else:
                # Use GROQ models
                return self._call_groq(prompt, system_prompt, model, temperature, max_tokens, **kwargs)
                
        except Exception as e:
            logger.error(f"Error in unified LLM client: {e}")
            # Fallback to GROQ primary model
            return self._call_groq(prompt, system_prompt, PRIMARY_MODEL, temperature, max_tokens, **kwargs)
    
    def _call_openai(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Call OpenAI o3-mini model"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.openai_client.chat.completions.create(
                model="o3-mini",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error calling OpenAI: {e}")
            raise
    
    def _call_gemma(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Call Gemma 3 12B service"""
        try:
            # Combine system prompt and user prompt for Gemma
            if system_prompt:
                combined_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
            else:
                combined_prompt = prompt
            
            return ask_gemma(combined_prompt, streaming=False)
            
        except Exception as e:
            logger.error(f"Error calling Gemma: {e}")
            raise
    
    def _call_groq(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: str = PRIMARY_MODEL,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Call GROQ models"""
        try:
            if system_prompt:
                return groq_client.generate_with_system_prompt(
                    system_prompt=system_prompt,
                    user_message=prompt,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
            else:
                messages = [{"role": "user", "content": prompt}]
                return groq_client.chat_completion(
                    messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
                
        except Exception as e:
            logger.error(f"Error calling GROQ: {e}")
            raise

# Global unified client instance
unified_llm_client = UnifiedLLMClient()

# Convenience functions for different use cases
def generate_hypothesis(prompt: str, system_prompt: Optional[str] = None) -> str:
    """Generate creative hypotheses using Gemma 3 12B"""
    return unified_llm_client.generate_response(
        prompt, system_prompt, model_strategy="creative_generation", temperature=0.8
    )

def analyze_hypothesis(prompt: str, system_prompt: Optional[str] = None) -> str:
    """Analyze hypotheses using OpenAI o3-mini for precision"""
    return unified_llm_client.generate_response(
        prompt, system_prompt, model_strategy="precise_analysis", temperature=0.3
    )

def complex_reasoning(prompt: str, system_prompt: Optional[str] = None) -> str:
    """Complex reasoning using GROQ Llama 3.3 70B"""
    return unified_llm_client.generate_response(
        prompt, system_prompt, model_strategy="complex_reasoning", temperature=0.7
    )

def quick_processing(prompt: str, system_prompt: Optional[str] = None) -> str:
    """Quick processing using GROQ Gemma 2 9B"""
    return unified_llm_client.generate_response(
        prompt, system_prompt, model_strategy="fast_operations", temperature=0.5
    )