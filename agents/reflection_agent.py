from typing import Dict, Any, List
import json

from agents.base_agent import BaseCoScientistAgent
from utils.adk_tools import critique_hypothesis_tool

# Import prompts with fallback for testing
try:
    from prompts import AgentPrompts, PromptTemplates
except ImportError:
    from test_prompts import MockAgentPrompts as AgentPrompts, MockPromptTemplates as PromptTemplates

class ReflectionAgent(BaseCoScientistAgent):
    """Agent responsible for critiquing and evaluating scientific hypotheses using GROQ Llama 3.3 70B"""
    
    def __init__(self):
        super().__init__(
            name="reflection_agent",
            description="Critiques and evaluates scientific hypotheses for validity, novelty, and feasibility",
            model="llama-3.3-70b-versatile",  # Use GROQ Llama 3.3 70B for precise reasoning
            tools=[critique_hypothesis_tool]
        )
    
    def get_system_prompt(self) -> str:
        return AgentPrompts.REFLECTION_AGENT

    def critique_hypotheses(self, hypotheses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Critique a list of scientific hypotheses
        
        Args:
            hypotheses: List of hypothesis dictionaries
            
        Returns:
            List of critique dictionaries
        """
        # Format hypotheses for evaluation
        hypotheses_text = ""
        for i, hyp in enumerate(hypotheses, 1):
            hypotheses_text += f"\nHypothesis {i} (ID: {hyp.get('id', 'unknown')}):\n"
            hypotheses_text += f"Title: {hyp.get('title', 'N/A')}\n"
            hypotheses_text += f"Description: {hyp.get('description', 'N/A')}\n"
            hypotheses_text += f"Reasoning: {hyp.get('reasoning', 'N/A')}\n"
            hypotheses_text += f"Research Approach: {hyp.get('research_approach', 'N/A')}\n"
            hypotheses_text += "-" * 50
        
        evaluation_query = PromptTemplates.hypothesis_critique_template(hypotheses_text)

        result = self.run(evaluation_query)
        
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
                end_idx = output.rfind("}")
                json_content = output[start_idx:end_idx + 1]
            
            parsed_output = json.loads(json_content)
            
            # Extract critiques array
            if "critiques" in parsed_output:
                critiques = parsed_output["critiques"]
            elif isinstance(parsed_output, list):
                critiques = parsed_output
            else:
                critiques = [parsed_output]
            
            # Ensure all critiques have required fields
            processed_critiques = []
            for i, critique in enumerate(critiques):
                processed_critique = {
                    "hypothesis_id": critique.get("hypothesis_id", hypotheses[i]["id"] if i < len(hypotheses) else f"unknown_{i}"),
                    "overall_assessment": critique.get("overall_assessment", "Assessment pending"),
                    "validity_score": float(critique.get("validity_score", 0.5)),
                    "novelty_score": float(critique.get("novelty_score", 0.5)),
                    "feasibility_score": float(critique.get("feasibility_score", 0.5)),
                    "impact_score": float(critique.get("impact_score", 0.5)),
                    "specific_critiques": critique.get("specific_critiques", []),
                    "suggestions": critique.get("suggestions", []),
                    "agent_metadata": result["metadata"]
                }
                processed_critiques.append(processed_critique)
            
            return processed_critiques
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Fallback: create basic critiques
            fallback_critiques = []
            for hyp in hypotheses:
                fallback_critiques.append({
                    "hypothesis_id": hyp.get("id", "unknown"),
                    "overall_assessment": "Automated critique analysis needed",
                    "validity_score": 0.7,
                    "novelty_score": 0.6,
                    "feasibility_score": 0.8,
                    "impact_score": 0.7,
                    "specific_critiques": ["Detailed analysis pending"],
                    "suggestions": ["Refine experimental methodology"],
                    "agent_metadata": result["metadata"]
                })
            return fallback_critiques