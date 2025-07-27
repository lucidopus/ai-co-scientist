from utils.models import (
    QueryRequest,
    QueryResponse,
)
from agents.workflow_orchestrator import AICoScientistWorkflow
from agents.enhanced_workflow_orchestrator import EnhancedAICoScientistWorkflow


def generate_hypotheses_pipeline(request: QueryRequest, use_smart_orchestration: bool = True) -> QueryResponse:
    """
    Main pipeline for generating scientific hypotheses using ADK-based multi-agent system.
    
    This function implements the complete AI co-scientist workflow with intelligent model assignment:
    1. Analyzes workflow with Claude Opus 4 orchestrator for optimal model selection
    2. Generates novel scientific hypotheses using assigned model
    3. Retrieves related knowledge using assigned model + search
    4. Critiques and evaluates them using assigned model
    5. Ranks them by multiple criteria using assigned model
    6. Evolves top hypotheses using assigned model
    7. Performs final meta-review using assigned model
    
    Args:
        request: QueryRequest with research query and parameters
        use_smart_orchestration: Whether to use intelligent model assignment (default: True)
        
    Returns:
        QueryResponse with generated hypotheses and processing details
    """
    
    if use_smart_orchestration:
        # Initialize the enhanced workflow orchestrator with intelligent model assignment
        workflow = EnhancedAICoScientistWorkflow()
    else:
        # Use traditional workflow with fixed model assignments
        workflow = AICoScientistWorkflow()
    
    # Process the query through the complete multi-agent pipeline
    response = workflow.process_scientific_query(request)
    
    return response


def generate_hypotheses_pipeline_legacy(request: QueryRequest) -> QueryResponse:
    """
    Legacy pipeline for generating scientific hypotheses with fixed model assignments.
    
    This function implements the original AI co-scientist workflow that:
    1. Generates novel scientific hypotheses (Gemma 3 12B)
    2. Retrieves related knowledge (Gemma 2 9B + search)
    3. Critiques and evaluates them (OpenAI o3-mini)
    4. Ranks them by multiple criteria (Gemma 2 9B)
    5. Evolves top hypotheses (Llama 3.3 70B)
    6. Performs final meta-review (OpenAI o3-mini)
    """
    
    # Initialize the original ADK-based workflow orchestrator
    workflow = AICoScientistWorkflow()
    
    # Process the query through the complete multi-agent pipeline
    response = workflow.process_scientific_query(request)
    
    return response

 