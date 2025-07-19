from utils.models import (
    QueryRequest,
    QueryResponse,
)
from agents.workflow_orchestrator import AICoScientistWorkflow


def generate_hypotheses_pipeline(request: QueryRequest) -> QueryResponse:
    """
    Main pipeline for generating scientific hypotheses using ADK-based multi-agent system.
    
    This function implements the complete AI co-scientist workflow that:
    1. Generates novel scientific hypotheses (Gemma 3 12B)
    2. Retrieves related knowledge (Gemma 2 9B + search)
    3. Critiques and evaluates them (OpenAI o3-mini)
    4. Ranks them by multiple criteria (Gemma 2 9B)
    5. Evolves top hypotheses (Llama 3.3 70B)
    6. Performs final meta-review (OpenAI o3-mini)
    """
    
    # Initialize the ADK-based workflow orchestrator
    workflow = AICoScientistWorkflow()
    
    # Process the query through the complete multi-agent pipeline
    response = workflow.process_scientific_query(request)
    
    return response

 