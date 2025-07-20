from typing import Dict, Any, List, Tuple
import json

from agents.base_agent import BaseCoScientistAgent
from utils.adk_tools import rank_hypotheses_tool

# Import prompts with fallback for testing
try:
    from prompts import AgentPrompts, PromptTemplates
except ImportError:
    from test_prompts import MockAgentPrompts as AgentPrompts, MockPromptTemplates as PromptTemplates

class RankingAgent(BaseCoScientistAgent):
    """Agent responsible for ranking and scoring scientific hypotheses using GROQ Gemma2 9B"""
    
    def __init__(self):
        super().__init__(
            name="ranking_agent",
            description="Ranks and scores scientific hypotheses based on multiple criteria",
            model="qwen/qwen3-32b",  # Use GROQ Gemma2 9B for fast ranking operations
            tools=[rank_hypotheses_tool]
        )
    
    def get_system_prompt(self) -> str:
        return AgentPrompts.RANKING_AGENT

    def rank_hypotheses(
        self, 
        hypotheses: List[Dict[str, Any]], 
        critiques: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Rank a list of scientific hypotheses with their critiques
        
        Args:
            hypotheses: List of hypothesis dictionaries
            critiques: Optional list of critique dictionaries
            
        Returns:
            List of ranked hypothesis dictionaries with scores
        """
        # Format hypotheses and critiques for ranking
        ranking_input = "HYPOTHESES TO RANK:\n\n"
        
        for i, hyp in enumerate(hypotheses, 1):
            ranking_input += f"Hypothesis {i} (ID: {hyp.get('id', 'unknown')}):\n"
            ranking_input += f"Title: {hyp.get('title', 'N/A')}\n"
            ranking_input += f"Description: {hyp.get('description', 'N/A')}\n"
            ranking_input += f"Reasoning: {hyp.get('reasoning', 'N/A')}\n"
            
            # Add critique information if available
            if critiques:
                critique = next((c for c in critiques if c.get("hypothesis_id") == hyp.get("id")), None)
                if critique:
                    ranking_input += f"Critique Scores: Validity={critique.get('validity_score', 'N/A')}, "
                    ranking_input += f"Novelty={critique.get('novelty_score', 'N/A')}, "
                    ranking_input += f"Feasibility={critique.get('feasibility_score', 'N/A')}, "
                    ranking_input += f"Impact={critique.get('impact_score', 'N/A')}\n"
                    ranking_input += f"Assessment: {critique.get('overall_assessment', 'N/A')}\n"
            
            ranking_input += "-" * 60 + "\n"
        
        ranking_query = PromptTemplates.hypothesis_ranking_template(ranking_input)

        result = self.run(ranking_query)
        
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
            
            # Extract rankings
            if "rankings" in parsed_output:
                rankings = parsed_output["rankings"]
            elif isinstance(parsed_output, list):
                rankings = parsed_output
            else:
                rankings = [parsed_output]
            
            # Merge ranking data with original hypotheses
            ranked_hypotheses = []
            for ranking in rankings:
                hypothesis_id = ranking.get("hypothesis_id")
                original_hyp = next((h for h in hypotheses if h.get("id") == hypothesis_id), None)
                
                if original_hyp:
                    ranked_hyp = original_hyp.copy()
                    ranked_hyp.update({
                        "rank": ranking.get("rank", 999),
                        "final_score": float(ranking.get("final_score", 0.5)),
                        "criterion_scores": ranking.get("criterion_scores", {}),
                        "ranking_justification": ranking.get("justification", ""),
                        "ranking_confidence": float(ranking.get("confidence", 0.5)),
                        "ranking_metadata": result["metadata"]
                    })
                    ranked_hypotheses.append(ranked_hyp)
            
            # Sort by rank
            ranked_hypotheses.sort(key=lambda x: x.get("rank", 999))
            
            return ranked_hypotheses
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Fallback: simple scoring based on critiques if available
            scored_hypotheses = []
            
            for i, hyp in enumerate(hypotheses):
                # Calculate fallback score
                if critiques:
                    critique = next((c for c in critiques if c.get("hypothesis_id") == hyp.get("id")), None)
                    if critique:
                        # Use critique scores for ranking
                        validity = critique.get("validity_score", 0.5)
                        novelty = critique.get("novelty_score", 0.5)
                        feasibility = critique.get("feasibility_score", 0.5)
                        impact = critique.get("impact_score", 0.5)
                        
                        # Weighted average
                        final_score = (validity * 0.25 + novelty * 0.25 + 
                                     feasibility * 0.20 + impact * 0.20 + 0.8 * 0.10)
                    else:
                        final_score = 0.6  # Default score
                else:
                    final_score = 0.7 - (i * 0.1)  # Decreasing scores
                
                ranked_hyp = hyp.copy()
                ranked_hyp.update({
                    "rank": i + 1,
                    "final_score": final_score,
                    "criterion_scores": {
                        "validity": 0.7,
                        "novelty": 0.6,
                        "feasibility": 0.8,
                        "impact": 0.7,
                        "clarity": 0.8
                    },
                    "ranking_justification": "Fallback ranking based on available data",
                    "ranking_confidence": 0.6,
                    "ranking_metadata": result["metadata"]
                })
                scored_hypotheses.append(ranked_hyp)
            
            return scored_hypotheses