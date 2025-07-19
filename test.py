#!/usr/bin/env python3
"""
Test script for the AI Co-Scientist system
"""

from utils.models import QueryRequest
from utils.pipelines import generate_hypotheses_pipeline
from utils.logging_config import setup_logging

# Setup logging
logger = setup_logging()

def test_scientific_query():
    """Test the AI Co-Scientist system with a sample scientific query"""
    
    # Sample scientific queries to test
    test_queries = [
        {
            "query": "How can we develop more effective treatments for antibiotic-resistant bacterial infections?",
            "max_hypotheses": 3
        },
        {
            "query": "What novel approaches could accelerate the development of sustainable energy storage solutions?",
            "max_hypotheses": 2
        }
    ]
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"TEST CASE {i}: {test_case['query']}")
        print(f"{'='*80}")
        
        try:
            # Create request
            request = QueryRequest(
                query=test_case["query"],
                max_hypotheses=test_case["max_hypotheses"]
            )
            
            logger.info(f"Testing query: {request.query}")
            
            # Process through pipeline
            response = generate_hypotheses_pipeline(request)
            
            # Display results
            print(f"\nQuery ID: {response.query_id}")
            print(f"Processing Time: {response.total_processing_time:.2f} seconds")
            print(f"Generated Hypotheses: {len(response.hypotheses)}")
            
            print(f"\nSUMMARY:")
            print(response.summary)
            
            print(f"\nHYPOTHESES:")
            for j, hypothesis in enumerate(response.hypotheses, 1):
                print(f"\n--- Hypothesis {j} ---")
                print(f"Title: {hypothesis.title}")
                print(f"Description: {hypothesis.description[:200]}...")
                print(f"Novelty Score: {hypothesis.novelty_score:.2f}")
                print(f"Feasibility Score: {hypothesis.feasibility_score:.2f}")
                print(f"Confidence Score: {hypothesis.confidence_score:.2f}")
            
            print(f"\nPROCESSING STEPS:")
            for step in response.processing_steps:
                print(f"- {step.step_name}: {step.duration_seconds:.2f}s ({step.status})")
                for output in step.agent_outputs:
                    print(f"  * {output.agent_name}: {output.output}")
            
            print(f"\nRECOMMENDATIONS:")
            for rec in response.recommendations:
                print(f"- {rec}")
            
            logger.info(f"Test case {i} completed successfully")
            
        except Exception as e:
            logger.error(f"Test case {i} failed: {str(e)}", exc_info=True)
            print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    print("AI Co-Scientist System Test")
    print("Testing multi-agent workflow with real LLM APIs...")
    
    test_scientific_query()
    
    print(f"\n{'='*80}")
    print("Test completed. Check logs for detailed information.")
    print(f"{'='*80}")