from typing import Optional, List, Dict, Any
from datetime import datetime

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(
        description="The scientific research query or question",
    )
    max_hypotheses: int = Field(
        default=5,
        description="Maximum number of hypotheses to generate",
    )


class Hypothesis(BaseModel):
    id: str = Field(description="Unique identifier for the hypothesis")
    title: str = Field(description="Title of the hypothesis")
    description: str = Field(description="Detailed description of the hypothesis")
    reasoning: str = Field(description="Scientific reasoning behind the hypothesis")
    novelty_score: float = Field(description="Novelty score (0.0 to 1.0)")
    feasibility_score: float = Field(description="Feasibility score (0.0 to 1.0)")
    confidence_score: float = Field(description="Confidence score (0.0 to 1.0)")
    experimental_plan: str = Field(description="Step-by-step experimental plan")
    citations: List[str] = Field(description="Relevant scientific citations")


class AgentOutput(BaseModel):
    agent_name: str = Field(description="Name of the AI agent")
    output: str = Field(description="Output from the agent")
    metadata: Dict[str, Any] = Field(description="Additional metadata from the agent")


class ProcessingStep(BaseModel):
    step_name: str = Field(description="Name of the processing step")
    status: str = Field(description="Status of the processing step")
    start_time: datetime = Field(description="Start time of the step")
    end_time: datetime = Field(description="End time of the step")
    duration_seconds: float = Field(description="Duration of the step in seconds")
    agent_outputs: List[AgentOutput] = Field(description="Outputs from agents in this step")


class QueryResponse(BaseModel):
    query_id: str = Field(description="Unique identifier for the query")
    original_query: str = Field(description="The original research query")
    hypotheses: List[Hypothesis] = Field(description="Generated hypotheses")
    processing_steps: List[ProcessingStep] = Field(description="Processing steps taken")
    total_processing_time: float = Field(description="Total processing time in seconds")
    summary: str = Field(description="Summary of the results")
    recommendations: List[str] = Field(description="Research recommendations")


class SampleQueryResponse(BaseModel):
    generated_query: str = Field(description="The automatically generated scientific query")

class ErrorResponse(BaseModel):
    error: str = Field(description="Error message")
    error_code: str = Field(description="Error code")
    details: str = Field(description="Additional error details")


class SampleQueryResponse(BaseModel):
    generated_query: str = Field(description="The automatically generated scientific query")


class HealthResponse(BaseModel):
    status: str = Field(description="Health status")
    version: str = Field(description="API version") 