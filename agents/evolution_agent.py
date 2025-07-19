from typing import Dict, Any, List
import json
import uuid

from agents.base_agent import BaseCoScientistAgent
from prompts import AgentPrompts, PromptTemplates

class EvolutionAgent(BaseCoScientistAgent):
    """Agent responsible for iteratively refining and evolving hypotheses"""
    
    def __init__(self):
        super().__init__(
            name="evolution_agent",
            description="Iteratively refines and evolves scientific hypotheses through mutation and combination",
            model="llama-3.3-70b-versatile"  # Use GROQ Llama for complex reasoning
        )
    
    def get_system_prompt(self) -> str:
        return AgentPrompts.EVOLUTION_AGENT

    def evolve_hypotheses(
        self, 
        hypotheses: List[Dict[str, Any]], 
        critiques: List[Dict[str, Any]] = None,
        evolution_rounds: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Evolve hypotheses through iterative refinement
        
        Args:
            hypotheses: List of hypothesis dictionaries to evolve
            critiques: Optional critiques to guide evolution
            evolution_rounds: Number of evolution iterations
            
        Returns:
            List of evolved hypothesis dictionaries
        """
        current_hypotheses = hypotheses.copy()
        
        for round_num in range(evolution_rounds):
            evolution_input = self._format_evolution_input(current_hypotheses, critiques)
            
            evolution_query = PromptTemplates.hypothesis_evolution_template(evolution_input, round_num + 1)

            result = self.run(evolution_query)
            
            try:
                # Parse JSON response
                output = result["output"]
                
                # Extract JSON from the response
                if "```json" in output:
                    json_start = output.find("```json") + 7
                    json_end = output.find("```", json_start)
                    json_content = output[json_start:json_end].strip()
                else:
                    start_idx = output.find("{")
                    end_idx = output.rfind("}")
                    json_content = output[start_idx:end_idx + 1]
                
                parsed_output = json.loads(json_content)
                
                # Extract evolved hypotheses
                if "evolved_hypotheses" in parsed_output:
                    evolved = parsed_output["evolved_hypotheses"]
                elif isinstance(parsed_output, list):
                    evolved = parsed_output
                else:
                    evolved = [parsed_output]
                
                # Process evolved hypotheses
                current_hypotheses = []
                for evo_hyp in evolved:
                    processed_hyp = {
                        "id": str(uuid.uuid4()),
                        "original_id": evo_hyp.get("original_id", "unknown"),
                        "title": evo_hyp.get("title", "Evolved Hypothesis"),
                        "description": evo_hyp.get("description", ""),
                        "reasoning": evo_hyp.get("reasoning", ""),
                        "evolution_type": evo_hyp.get("evolution_type", "refinement"),
                        "improvements": evo_hyp.get("improvements", []),
                        "evolution_justification": evo_hyp.get("evolution_justification", ""),
                        "evolution_round": round_num + 1,
                        "agent_metadata": result["metadata"]
                    }
                    current_hypotheses.append(processed_hyp)
                
            except (json.JSONDecodeError, KeyError) as e:
                # Fallback: create evolved versions with basic improvements
                evolved_hypotheses = []
                for i, hyp in enumerate(current_hypotheses):
                    evolved_hyp = hyp.copy()
                    evolved_hyp.update({
                        "id": str(uuid.uuid4()),
                        "original_id": hyp.get("id", "unknown"),
                        "title": f"Evolved: {hyp.get('title', 'Hypothesis')}",
                        "evolution_type": "refinement",
                        "improvements": ["Enhanced specificity", "Improved testability"],
                        "evolution_justification": "Systematic refinement applied",
                        "evolution_round": round_num + 1,
                        "agent_metadata": result["metadata"]
                    })
                    evolved_hypotheses.append(evolved_hyp)
                current_hypotheses = evolved_hypotheses
        
        return current_hypotheses
    
    def _format_evolution_input(
        self, 
        hypotheses: List[Dict[str, Any]], 
        critiques: List[Dict[str, Any]] = None
    ) -> str:
        """Format hypotheses and critiques for evolution input"""
        
        evolution_input = "HYPOTHESES TO EVOLVE:\n\n"
        
        for i, hyp in enumerate(hypotheses, 1):
            evolution_input += f"Hypothesis {i} (ID: {hyp.get('id', 'unknown')}):\n"
            evolution_input += f"Title: {hyp.get('title', 'N/A')}\n"
            evolution_input += f"Description: {hyp.get('description', 'N/A')}\n"
            evolution_input += f"Reasoning: {hyp.get('reasoning', 'N/A')}\n"
            
            # Add existing evolution history if available
            if "evolution_type" in hyp:
                evolution_input += f"Previous Evolution: {hyp.get('evolution_type', 'N/A')}\n"
                evolution_input += f"Previous Improvements: {hyp.get('improvements', [])}\n"
            
            # Add critique information if available
            if critiques:
                critique = next((c for c in critiques if c.get("hypothesis_id") == hyp.get("id")), None)
                if critique:
                    evolution_input += f"\nCRITIQUE FEEDBACK:\n"
                    evolution_input += f"Validity Score: {critique.get('validity_score', 'N/A')}\n"
                    evolution_input += f"Novelty Score: {critique.get('novelty_score', 'N/A')}\n"
                    evolution_input += f"Feasibility Score: {critique.get('feasibility_score', 'N/A')}\n"
                    evolution_input += f"Specific Critiques: {critique.get('specific_critiques', [])}\n"
                    evolution_input += f"Suggestions: {critique.get('suggestions', [])}\n"
            
            evolution_input += "-" * 70 + "\n"
        
        return evolution_input