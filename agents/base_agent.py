from typing import Dict, Any, List, Optional
import logging
from abc import ABC, abstractmethod

from utils.unified_llm_client import unified_llm_client

logger = logging.getLogger(__name__)

class BaseCoScientistAgent(ABC):
    """Base class for AI Co-Scientist agents"""
    
    def __init__(self, name: str, description: str, model: str = "llama-3.3-70b-versatile"):
        self.name = name
        self.description = description
        self.model = model
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent"""
        pass
    
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
            system_prompt = self.get_system_prompt()
            
            # Add context to the input if provided
            if context:
                enhanced_input = f"Context: {context}\n\nInput: {input_data}"
            else:
                enhanced_input = input_data
            
            # Generate response using unified LLM client
            strategy = "creative_generation" if self.model == "gemma3:12b" else "complex_reasoning"
            response = unified_llm_client.generate_response(
                prompt=enhanced_input,
                system_prompt=system_prompt,
                model_strategy=strategy,
                temperature=0.7
            )
            
            return {
                "agent_name": self.name,
                "output": response,
                "metadata": {
                    "model_used": self.model,
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