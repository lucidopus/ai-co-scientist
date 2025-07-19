from typing import Dict, Any, List, Optional
import logging
from abc import abstractmethod

from google.adk.agents import Agent

# Import with error handling for testing environments
try:
    from utils.helper import ask_gemma
except ImportError:
    ask_gemma = None

try:
    from utils.groq_client import groq_client
except (ImportError, ValueError):
    groq_client = None

logger = logging.getLogger(__name__)

class BaseCoScientistAgent(Agent):
    """Base class for AI Co-Scientist agents using Google ADK with multi-model support"""
    
    def __init__(self, name: str, description: str, model: str = "gemini-2.5-flash", instruction: str = "", tools: List = None):
        """
        Initialize ADK-based agent with multi-model support
        
        Args:
            name: Agent name
            description: Agent description  
            model: Model to use (supports deployed Gemma, GROQ models, etc.)
            instruction: System instruction for the agent
            tools: List of tools/functions the agent can use
        """
        # For ADK initialization, use a default model
        super().__init__(
            name=name,
            model="gemini-2.5-flash",  # ADK default, actual model handled in generate_response
            instruction=instruction or self.get_system_prompt(),
            tools=tools or []
        )
        self.description = description
        self._actual_model = model  # Store the actual model we want to use
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent - used as instruction in ADK"""
        pass
    
    def generate_response(self, prompt: str) -> str:
        """
        Generate response using the specified model (deployed Gemma, GROQ, etc.)
        
        Args:
            prompt: Input prompt to process
            
        Returns:
            Generated response text
        """
        try:
            system_prompt = self.get_system_prompt()
            
            if self._actual_model == "gemma3:12b":
                # Use deployed Gemma 12B via ask_gemma function
                if ask_gemma is None:
                    return f"[TEST MODE] Would use deployed Gemma 12B for: {prompt[:50]}..."
                
                if system_prompt:
                    combined_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
                else:
                    combined_prompt = prompt
                return ask_gemma(combined_prompt, streaming=False)
                
            elif self._actual_model.startswith(("llama-", "gemma2-", "qwen/")):
                # Use GROQ models
                if groq_client is None:
                    return f"[TEST MODE] Would use GROQ {self._actual_model} for: {prompt[:50]}..."
                
                return groq_client.generate_with_system_prompt(
                    system_prompt=system_prompt,
                    user_message=prompt,
                    model=self._actual_model,
                    temperature=0.7
                )
            else:
                # Fallback to ADK's default behavior
                try:
                    return super().generate_response(prompt)
                except Exception:
                    return f"[TEST MODE] Would use ADK default model for: {prompt[:50]}..."
                
        except Exception as e:
            logger.error(f"Error generating response in {self.name}: {e}")
            # Fallback to GROQ Llama as backup
            try:
                if groq_client is None:
                    return f"[TEST MODE] Fallback would use GROQ Llama for: {prompt[:50]}..."
                
                return groq_client.generate_with_system_prompt(
                    system_prompt=self.get_system_prompt(),
                    user_message=prompt,
                    model="llama-3.3-70b-versatile",
                    temperature=0.7
                )
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {fallback_error}")
                return f"[TEST MODE] Error: Unable to generate response - {str(e)}"
    
    def run(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run the agent with input data and optional context
        
        Args:
            input_data: The input to process
            context: Additional context for the agent
            
        Returns:
            Dictionary with agent output and metadata
        """
        try:
            # Add context to the input if provided
            if context:
                enhanced_input = f"Context: {context}\n\nInput: {input_data}"
            else:
                enhanced_input = input_data
            
            # Use our custom response generation
            response = self.generate_response(enhanced_input)
            
            return {
                "agent_name": self.name,
                "output": response,
                "metadata": {
                    "model_used": self._actual_model,
                    "input_length": len(input_data),
                    "output_length": len(response)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in agent {self.name}: {e}")
            return {
                "agent_name": self.name,
                "output": f"Error: {str(e)}",
                "metadata": {"error": True}
            }