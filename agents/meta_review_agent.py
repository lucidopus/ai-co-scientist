from typing import Dict, Any, List
import json

from agents.base_agent import BaseCoScientistAgent
from utils.adk_tools import plan_experiments_tool

# Import prompts with fallback for testing
try:
    from prompts import AgentPrompts, PromptTemplates
except ImportError:
    from test_prompts import MockAgentPrompts as AgentPrompts, MockPromptTemplates as PromptTemplates

class MetaReviewAgent(BaseCoScientistAgent):
    """Agent responsible for final review and experimental planning using GROQ Llama 3.3 70B"""
    
    def __init__(self):
        super().__init__(
            name="meta_review_agent",
            description="Performs final review and creates comprehensive experimental plans",
            model="llama-3.3-70b-versatile",  # Use GROQ Llama 3.3 70B for comprehensive final analysis
            tools=[plan_experiments_tool]
        )
    
    def get_system_prompt(self) -> str:
        return AgentPrompts.META_REVIEW_AGENT

    def final_review(
        self, 
        hypotheses: List[Dict[str, Any]], 
        critiques: List[Dict[str, Any]] = None,
        rankings: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform final meta-review of hypotheses and create experimental plans
        
        Args:
            hypotheses: List of final hypothesis dictionaries
            critiques: Optional critique data
            rankings: Optional ranking data
            
        Returns:
            Dictionary with final reviews and experimental plans
        """
        # Format comprehensive input for meta-review
        review_input = self._format_meta_review_input(hypotheses, critiques, rankings)
        
        meta_review_query = PromptTemplates.meta_review_template(review_input)

        result = self.run(meta_review_query)
        
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
            
            # Extract final reviews
            final_reviews = parsed_output.get("final_reviews", [])
            
            # Ensure all reviews have required fields
            processed_reviews = []
            for i, review in enumerate(final_reviews):
                processed_review = {
                    "hypothesis_id": review.get("hypothesis_id", hypotheses[i]["id"] if i < len(hypotheses) else f"unknown_{i}"),
                    "final_assessment": review.get("final_assessment", "Comprehensive review pending"),
                    "confidence_rating": float(review.get("confidence_rating", 0.7)),
                    "experimental_plan": review.get("experimental_plan", {}),
                    "resource_requirements": review.get("resource_requirements", {}),
                    "timeline": review.get("timeline", "Timeline to be determined"),
                    "risk_factors": review.get("risk_factors", []),
                    "success_metrics": review.get("success_metrics", []),
                    "collaboration_recommendations": review.get("collaboration_recommendations", []),
                    "agent_metadata": result["metadata"]
                }
                processed_reviews.append(processed_review)
            
            return {
                "final_reviews": processed_reviews,
                "research_priorities": parsed_output.get("research_priorities", "Prioritization analysis pending"),
                "overall_assessment": parsed_output.get("overall_assessment", "Overall portfolio assessment pending"),
                "meta_review_metadata": result["metadata"]
            }
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Fallback: create basic final reviews
            fallback_reviews = []
            for hyp in hypotheses:
                fallback_reviews.append({
                    "hypothesis_id": hyp.get("id", "unknown"),
                    "final_assessment": "Comprehensive meta-review analysis needed",
                    "confidence_rating": 0.7,
                    "experimental_plan": {
                        "phase_1": "Literature review and preliminary validation",
                        "phase_2": "Experimental design and pilot studies",
                        "phase_3": "Full implementation and validation"
                    },
                    "resource_requirements": {
                        "personnel": ["Research scientists", "Technical specialists"],
                        "equipment": ["Standard laboratory equipment"],
                        "funding": "Medium-scale research budget"
                    },
                    "timeline": "12-24 months for initial validation",
                    "risk_factors": ["Technical challenges", "Resource constraints"],
                    "success_metrics": ["Proof of concept demonstration", "Peer review publication"],
                    "collaboration_recommendations": ["Academic partnerships", "Industry collaboration"],
                    "agent_metadata": result["metadata"]
                })
            
            return {
                "final_reviews": fallback_reviews,
                "research_priorities": "All hypotheses show promise and warrant investigation",
                "overall_assessment": "Solid portfolio of research directions with good potential",
                "meta_review_metadata": result["metadata"]
            }
    
    def _format_meta_review_input(
        self, 
        hypotheses: List[Dict[str, Any]], 
        critiques: List[Dict[str, Any]] = None,
        rankings: List[Dict[str, Any]] = None
    ) -> str:
        """Format comprehensive input for meta-review"""
        
        review_input = "HYPOTHESES FOR FINAL META-REVIEW:\n\n"
        
        for i, hyp in enumerate(hypotheses, 1):
            review_input += f"Hypothesis {i} (ID: {hyp.get('id', 'unknown')}):\n"
            review_input += f"Title: {hyp.get('title', 'N/A')}\n"
            review_input += f"Description: {hyp.get('description', 'N/A')}\n"
            review_input += f"Reasoning: {hyp.get('reasoning', 'N/A')}\n"
            
            # Add ranking information if available
            if rankings:
                ranking = next((r for r in rankings if r.get("id") == hyp.get("id")), None)
                if ranking:
                    review_input += f"Rank: {ranking.get('rank', 'N/A')}\n"
                    review_input += f"Final Score: {ranking.get('final_score', 'N/A')}\n"
                    review_input += f"Ranking Justification: {ranking.get('ranking_justification', 'N/A')}\n"
            
            # Add critique information if available
            if critiques:
                critique = next((c for c in critiques if c.get("hypothesis_id") == hyp.get("id")), None)
                if critique:
                    review_input += f"\nCRITIQUE ANALYSIS:\n"
                    review_input += f"Overall Assessment: {critique.get('overall_assessment', 'N/A')}\n"
                    review_input += f"Scores - Validity: {critique.get('validity_score', 'N/A')}, "
                    review_input += f"Novelty: {critique.get('novelty_score', 'N/A')}, "
                    review_input += f"Feasibility: {critique.get('feasibility_score', 'N/A')}, "
                    review_input += f"Impact: {critique.get('impact_score', 'N/A')}\n"
                    review_input += f"Suggestions: {critique.get('suggestions', [])}\n"
            
            # Add evolution information if available
            if "evolution_type" in hyp:
                review_input += f"\nEVOLUTION HISTORY:\n"
                review_input += f"Evolution Type: {hyp.get('evolution_type', 'N/A')}\n"
                review_input += f"Improvements: {hyp.get('improvements', [])}\n"
                review_input += f"Evolution Justification: {hyp.get('evolution_justification', 'N/A')}\n"
            
            review_input += "=" * 80 + "\n"
        
        return review_input