import time
import uuid
from typing import List, Dict, Any

from utils.models import Hypothesis, ProcessingStep, AgentOutput
from utils.enums import ProcessingStatus, AgentType


def calculate_processing_cost(processing_steps: List[ProcessingStep]) -> float:
    """
    Calculate the total cost of processing based on agent usage.
    
    Args:
        processing_steps: List of processing steps with agent outputs
        
    Returns:
        Total cost in USD
    """
    total_cost = 0.0
    
    for step in processing_steps:
        for output in step.agent_outputs:
            # Simulate cost calculation based on agent type
            if output.agent_name == AgentType.GENERATION:
                total_cost += 0.02  # Generation agent cost
            elif output.agent_name == AgentType.REFLECTION:
                total_cost += 0.015  # Reflection agent cost
            elif output.agent_name == AgentType.RANKING:
                total_cost += 0.01  # Ranking agent cost
    
    return round(total_cost, 4)


def validate_hypothesis_scores(hypothesis: Hypothesis) -> bool:
    """
    Validate that hypothesis scores are within valid ranges.
    
    Args:
        hypothesis: Hypothesis object to validate
        
    Returns:
        True if scores are valid, False otherwise
    """
    scores = [
        hypothesis.novelty_score,
        hypothesis.feasibility_score,
        hypothesis.confidence_score
    ]
    
    return all(0.0 <= score <= 1.0 for score in scores)


def rank_hypotheses_by_score(hypotheses: List[Hypothesis], score_type: str = "novelty") -> List[Hypothesis]:
    """
    Rank hypotheses by a specific score type.
    
    Args:
        hypotheses: List of hypotheses to rank
        score_type: Type of score to rank by ("novelty", "feasibility", "confidence")
        
    Returns:
        Sorted list of hypotheses
    """
    score_map = {
        "novelty": lambda h: h.novelty_score,
        "feasibility": lambda h: h.feasibility_score,
        "confidence": lambda h: h.confidence_score
    }
    
    if score_type not in score_map:
        raise ValueError(f"Invalid score type: {score_type}")
    
    return sorted(hypotheses, key=score_map[score_type], reverse=True)


def generate_hypothesis_summary(hypotheses: List[Hypothesis]) -> str:
    """
    Generate a summary of the hypotheses.
    
    Args:
        hypotheses: List of hypotheses to summarize
        
    Returns:
        Summary string
    """
    if not hypotheses:
        return "No hypotheses generated."
    
    avg_novelty = sum(h.novelty_score for h in hypotheses) / len(hypotheses)
    avg_feasibility = sum(h.feasibility_score for h in hypotheses) / len(hypotheses)
    avg_confidence = sum(h.confidence_score for h in hypotheses) / len(hypotheses)
    
    return (
        f"Generated {len(hypotheses)} hypotheses with average scores: "
        f"Novelty: {avg_novelty:.2f}, Feasibility: {avg_feasibility:.2f}, "
        f"Confidence: {avg_confidence:.2f}"
    )


def extract_keywords_from_query(query: str) -> List[str]:
    """
    Extract key scientific keywords from a query.
    
    Args:
        query: Scientific query string
        
    Returns:
        List of extracted keywords
    """
    # Simple keyword extraction - could be enhanced with NLP
    keywords = []
    common_scientific_terms = [
        "biomarker", "drug", "therapy", "treatment", "disease", "cancer",
        "protein", "gene", "mutation", "clinical", "trial", "experiment",
        "analysis", "data", "model", "algorithm", "machine learning",
        "AI", "artificial intelligence", "quantum", "materials", "energy"
    ]
    
    query_lower = query.lower()
    for term in common_scientific_terms:
        if term in query_lower:
            keywords.append(term)
    
    return keywords


def format_experimental_plan(plan: str) -> str:
    """
    Format experimental plan for better readability.
    
    Args:
        plan: Raw experimental plan string
        
    Returns:
        Formatted experimental plan
    """
    if not plan:
        return "No experimental plan provided."
    
    # Ensure proper numbering and formatting
    lines = plan.strip().split('\n')
    formatted_lines = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        if line:
            # If line doesn't start with a number, add one
            if not line[0].isdigit():
                line = f"{i+1}. {line}"
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines) 