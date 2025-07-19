from typing import Dict, Any, Optional, List
import logging

# Note: This module is now deprecated in favor of ADK's native LLM handling
# All agents now use Google ADK's built-in model management
# Keeping this for backward compatibility during transition

logger = logging.getLogger(__name__)

class UnifiedLLMClient:
    """
    DEPRECATED: Unified client that can use GROQ, OpenAI, and Gemma models strategically
    
    This class is being phased out in favor of Google ADK's native LLM handling.
    All new agents should use ADK's Agent class with built-in model support.
    """
    
    def __init__(self):
        logger.warning("UnifiedLLMClient is deprecated. Use Google ADK agents instead.")
        
        # Model strategies - now primarily for reference
        self.model_strategies = {
            "complex_reasoning": "gemini-2.5-flash",        # ADK uses Gemini
            "fast_operations": "gemini-2.5-flash",          # ADK uses Gemini  
            "creative_generation": "gemini-2.5-flash",      # ADK uses Gemini
            "precise_analysis": "gemini-2.5-flash",         # ADK uses Gemini
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
        DEPRECATED: Generate response using the best model for the given strategy
        
        This method is deprecated. Use Google ADK agents instead.
        """
        logger.error("UnifiedLLMClient.generate_response is deprecated. Use ADK agents.")
        raise DeprecationWarning(
            "UnifiedLLMClient is deprecated. "
            "Use Google ADK agents with built-in model support instead."
        )
    
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