# 🚀 Feature Request: Auto Query Generation Endpoint

## 📋 Issue Summary

**Title:** Add `/sample` endpoint for automatic scientific query generation using Gemma 3 12B

**Type:** Feature Request  
**Priority:** High  
**Labels:** `enhancement`, `api`, `gemma`, `query-generation`  
**Assignee:** TBD  
**Milestone:** v1.1.0  

## 🎯 Objective

Implement an automated query generation system that creates high-quality scientific research queries suitable for testing the AI Co-Scientist hypothesis generation pipeline. This will provide users with example queries that demonstrate the system's capabilities across diverse scientific domains.

## 🔧 Technical Requirements

### New Endpoint
- **Path:** `GET /sample`
- **Method:** GET
- **Authentication:** Required (API key)
- **Input:** None (no request body)
- **Output:** Generated scientific query with metadata

### Implementation Details

#### 1. New Model Definition
Add to `utils/models.py`:
```python
class SampleQueryResponse(BaseModel):
    query_id: str = Field(description="Unique identifier for the generated query")
    generated_query: str = Field(description="The automatically generated scientific query")
    domain: str = Field(description="Primary scientific domain of the query")
    complexity_level: str = Field(description="Complexity level: basic/intermediate/advanced")
    estimated_hypotheses: int = Field(description="Estimated number of hypotheses this query could generate")
    generation_metadata: Dict[str, Any] = Field(description="Metadata about the generation process")
    timestamp: datetime = Field(description="When the query was generated")
```

#### 2. Query Generation Prompt
Add to `prompts.py` in the `AgentPrompts` class:
```python
QUERY_GENERATION_AGENT = """You are a scientific query generation agent for an AI Co-Scientist system. Your role is to create diverse, high-quality scientific research queries that can generate meaningful hypotheses.

QUERY GENERATION GUIDELINES:
1. **Diversity**: Generate queries across different scientific domains (biology, chemistry, physics, engineering, medicine, environmental science, etc.)
2. **Specificity**: Create focused, well-defined research questions that can lead to testable hypotheses
3. **Novelty**: Focus on emerging areas, interdisciplinary approaches, and cutting-edge challenges
4. **Feasibility**: Ensure queries can be addressed with current or near-future technology
5. **Impact**: Prioritize queries with potential for significant scientific or societal impact
6. **Clarity**: Write clear, unambiguous questions that researchers can understand and build upon

QUERY STRUCTURE REQUIREMENTS:
- Start with a clear research question or challenge
- Include specific constraints, focus areas, or methodologies when relevant
- Mention practical considerations (cost, time, equipment, etc.) when appropriate
- Specify target applications or outcomes when beneficial
- Use precise scientific terminology while remaining accessible

DOMAIN EXAMPLES:
- **Biomedical**: "How can we develop targeted therapies for rare genetic disorders using CRISPR-based approaches?"
- **Materials Science**: "What novel composite materials could improve energy storage efficiency in electric vehicles?"
- **Environmental**: "How can we design bio-inspired filtration systems for microplastic removal from water sources?"
- **AI/ML**: "Can we develop interpretable machine learning models for predicting protein folding intermediates?"
- **Energy**: "What innovative approaches could enable scalable fusion energy production using alternative confinement methods?"

OUTPUT FORMAT:
Generate a single high-quality query in this JSON structure:
{
  "generated_query": "Complete scientific research question with context and constraints",
  "domain": "Primary scientific domain (e.g., 'Biomedical', 'Materials Science', 'Environmental Science')",
  "subdomain": "Specific subfield (e.g., 'Genetic Engineering', 'Energy Storage', 'Water Treatment')",
  "complexity_level": "basic/intermediate/advanced",
  "estimated_hypotheses": 3-8,
  "key_concepts": ["concept1", "concept2", "concept3"],
  "research_approach": "Brief description of likely research methodology",
  "potential_impact": "Expected scientific or societal impact",
  "feasibility_factors": ["factor1", "factor2"],
  "interdisciplinary_elements": ["field1", "field2"]
}

Generate one diverse, high-quality scientific query that would be excellent for testing hypothesis generation capabilities."""
```

#### 3. Helper Function
Add to `utils/helper.py`:
```python
def generate_sample_query() -> dict:
    """
    Generate a sample scientific query using the deployed Gemma 3 12B model.
    
    Returns:
        dict: Generated query with metadata
    """
    from utils.config import GEMMA_SERVICE_URL
    import uuid
    from datetime import datetime
    
    if GEMMA_SERVICE_URL is None:
        raise ValueError("GEMMA_SERVICE_URL not configured")
    
    # Get the query generation prompt
    from prompts import AgentPrompts
    prompt = AgentPrompts.QUERY_GENERATION_AGENT
    
    try:
        # Call Gemma 3 12B for query generation
        response = ask_gemma(prompt, streaming=False)
        
        # Parse the JSON response
        import json
        query_data = json.loads(response)
        
        # Add metadata
        query_data["query_id"] = str(uuid.uuid4())
        query_data["timestamp"] = datetime.now().isoformat()
        
        return query_data
        
    except Exception as e:
        raise Exception(f"Error generating sample query: {str(e)}")
```

#### 4. API Endpoint
Add to `main.py`:
```python
@app.get(
    path="/sample",
    tags=["AI Co-Scientist"],
    response_model=SampleQueryResponse,
    response_description="Generated Sample Query",
    description="Generate a sample scientific query for testing the hypothesis generation system",
    name="Generate Sample Query",
)
async def generate_sample_query_endpoint(
    api_key: str = Depends(get_api_key),
):
    """
    Generate a sample scientific query using the deployed Gemma 3 12B model.
    
    This endpoint creates diverse, high-quality scientific research queries
    suitable for testing the AI Co-Scientist hypothesis generation pipeline.
    """
    
    try:
        logger.info("Generating sample scientific query")
        
        # Generate query using Gemma 3 12B
        query_data = generate_sample_query()
        
        # Create response object
        response = SampleQueryResponse(
            query_id=query_data["query_id"],
            generated_query=query_data["generated_query"],
            domain=query_data["domain"],
            complexity_level=query_data["complexity_level"],
            estimated_hypotheses=query_data["estimated_hypotheses"],
            generation_metadata={
                "subdomain": query_data.get("subdomain"),
                "key_concepts": query_data.get("key_concepts", []),
                "research_approach": query_data.get("research_approach"),
                "potential_impact": query_data.get("potential_impact"),
                "feasibility_factors": query_data.get("feasibility_factors", []),
                "interdisciplinary_elements": query_data.get("interdisciplinary_elements", [])
            },
            timestamp=datetime.fromisoformat(query_data["timestamp"])
        )
        
        logger.info(f"Successfully generated sample query in domain: {query_data['domain']}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating sample query: {str(e)}")
        raise FastAPIHTTPException(
            status_code=500,
            detail=f"Failed to generate sample query: {str(e)}"
        )
```

## 📝 Example Queries

The system should generate queries similar to these examples across diverse domains:

### Biomedical & Health
- "How can we develop targeted therapies for rare genetic disorders using CRISPR-based approaches? Focus on methods that can be tested in vitro and validated in animal models."
- "What novel strategies can be developed to overcome antibiotic resistance in Gram-negative bacteria, focusing on mechanisms that disrupt bacterial biofilm formation or quorum sensing?"

### Materials & Energy
- "Can we find simple modifications or coatings that extend the lifespan of lithium-ion batteries in everyday devices? Focus on methods that are low-cost and feasible for small electronics like phones or sensors."
- "What novel approaches could accelerate the development of sustainable energy storage solutions using bio-inspired materials?"

### Environmental & Sustainability
- "I want to find better ways to keep food fresh without using artificial preservatives. Can we discover natural compounds or packaging materials that slow down food spoilage? Focus on ideas that can be tested with simple lab experiments."

### AI & Computational Science
- "Can language models trained on protein sequences generate valid intermediate folding states that align with known molecular dynamics simulations?"
- "How might AI be used to advance climate change research and mitigation strategies through improved prediction models?"

### Interdisciplinary
- "What novel strategies can be developed to overcome antibiotic resistance in Gram-negative bacteria, focusing on mechanisms that disrupt bacterial biofilm formation or quorum sensing?"
- "How can we design bio-inspired filtration systems for microplastic removal from water sources using nanotechnology and biomimicry principles?"

## 🧪 Testing Requirements

### Unit Tests
- Test query generation with different prompt variations
- Validate JSON response parsing
- Test error handling for malformed responses
- Verify domain diversity across multiple generations

### Integration Tests
- Test endpoint with valid API key
- Test endpoint without API key (should fail)
- Test response format matches expected schema
- Test query quality and relevance

### Manual Testing
- Generate 10+ sample queries and verify quality
- Test queries across different scientific domains
- Verify generated queries work well with `/query` endpoint
- Check response times and performance

## 📊 Success Metrics

1. **Query Quality**: Generated queries should be clear, specific, and scientifically sound
2. **Domain Diversity**: Queries should span at least 8 different scientific domains
3. **Response Time**: Query generation should complete within 30 seconds
4. **Success Rate**: 95%+ of generated queries should be valid JSON and parseable
5. **User Satisfaction**: Generated queries should be useful for testing the system

## 🔄 Implementation Steps

1. **Phase 1**: Add new model definition to `utils/models.py`
2. **Phase 2**: Add query generation prompt to `prompts.py`
3. **Phase 3**: Implement helper function in `utils/helper.py`
4. **Phase 4**: Add API endpoint to `main.py`
5. **Phase 5**: Write comprehensive tests
6. **Phase 6**: Update documentation and examples

## 📚 Documentation Updates

- Update API documentation with new endpoint
- Add example usage in README
- Create integration guide for the sample query feature
- Update OpenAPI schema

## 🚨 Error Handling

- Handle Gemma service unavailability
- Handle malformed JSON responses
- Handle timeout scenarios
- Provide meaningful error messages
- Log all generation attempts and failures

## 🔒 Security Considerations

- Ensure API key authentication is enforced
- Validate all generated content before returning
- Implement rate limiting if needed
- Log generation attempts for monitoring

## 📈 Future Enhancements

1. **Query Categories**: Allow filtering by scientific domain
2. **Complexity Levels**: Generate queries of specific complexity
3. **Custom Constraints**: Allow users to specify focus areas
4. **Query History**: Store and retrieve previously generated queries
5. **Quality Feedback**: Allow users to rate generated queries

## 🎯 Acceptance Criteria

- [ ] `/sample` endpoint returns valid scientific queries
- [ ] Generated queries work seamlessly with `/query` endpoint
- [ ] Queries span diverse scientific domains
- [ ] Response format matches `SampleQueryResponse` schema
- [ ] Proper error handling and logging implemented
- [ ] Comprehensive test coverage
- [ ] Documentation updated
- [ ] Performance meets requirements (<30s response time)

## 🔗 Related Issues

- None currently identified

## 📝 Notes

- This feature will significantly improve user experience by providing ready-to-use examples
- The generated queries should demonstrate the system's capabilities across different scientific fields
- Consider implementing query caching to improve performance for repeated requests
- Monitor usage patterns to optimize the generation prompt over time 