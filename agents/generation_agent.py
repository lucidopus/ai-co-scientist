from typing import Dict, Any, List
import json
import uuid

from agents.base_agent import BaseCoScientistAgent
from utils.adk_tools import generate_hypotheses_tool

# Import prompts with fallback for testing
try:
    from prompts import AgentPrompts, PromptTemplates
except ImportError:
    from test_prompts import MockAgentPrompts as AgentPrompts, MockPromptTemplates as PromptTemplates

try:
    from utils.helper import ask_gemma
except ImportError:
    ask_gemma = None

class GenerationAgent(BaseCoScientistAgent):
    """Agent responsible for generating novel scientific hypotheses using deployed Gemma 12B"""
    
    def __init__(self):
        super().__init__(
            name="generation_agent",
            description="Generates novel scientific hypotheses based on research queries",
            model="gemma3:12b",  # Use deployed Gemma 12B via ask_gemma function
            tools=[generate_hypotheses_tool]
        )
    
    def get_system_prompt(self) -> str:
        return AgentPrompts.GENERATION_AGENT

    def generate_hypotheses(self, research_query: str, max_hypotheses: int = 5) -> List[Dict[str, Any]]:
        """
        Generate scientific hypotheses for a research query
        
        Args:
            research_query: The scientific research question or goal
            max_hypotheses: Maximum number of hypotheses to generate
            
        Returns:
            List of hypothesis dictionaries
        """
        enhanced_query = PromptTemplates.hypothesis_generation_template(research_query, max_hypotheses)

        result = self.run(enhanced_query)
        
        try:
            # Parse JSON response
            output = result["output"]
            
            # Extract JSON from the response
            if "```json" in output:
                json_start = output.find("```json") + 7
                json_end = output.find("```", json_start)
                json_content = output[json_start:json_end].strip()
            else:
                # Try to find JSON in the response
                start_idx = output.find("{")
                if start_idx == -1:
                    start_idx = output.find("[")
                end_idx = output.rfind("}")
                if end_idx == -1:
                    end_idx = output.rfind("]")
                json_content = output[start_idx:end_idx + 1]
            
            parsed_output = json.loads(json_content)
            
            # Extract hypotheses array
            if "hypotheses" in parsed_output:
                hypotheses = parsed_output["hypotheses"]
            elif isinstance(parsed_output, list):
                hypotheses = parsed_output
            else:
                hypotheses = [parsed_output]
            
            # Add unique IDs and ensure all required fields
            processed_hypotheses = []
            for i, hyp in enumerate(hypotheses[:max_hypotheses]):
                processed_hyp = {
                    "id": str(uuid.uuid4()),
                    "title": hyp.get("title", f"Hypothesis {i+1}"),
                    "description": hyp.get("description", ""),
                    "reasoning": hyp.get("reasoning", ""),
                    "novelty_assessment": hyp.get("novelty_assessment", ""),
                    "research_approach": hyp.get("research_approach", ""),
                    "agent_metadata": result["metadata"]
                }
                processed_hypotheses.append(processed_hyp)
            
            return processed_hypotheses
            
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback: create a single hypothesis from the raw output
            return [{
                "id": str(uuid.uuid4()),
                "title": f"Generated Hypothesis for: {research_query[:50]}...",
                "description": result["output"][:500],
                "reasoning": "Generated using AI reasoning",
                "novelty_assessment": "Novel approach to research question",
                "research_approach": "Requires further experimental design",
                "agent_metadata": result["metadata"]
            }]