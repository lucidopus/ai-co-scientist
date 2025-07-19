import os
import logging
import json
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Security, Depends, HTTPException as FastAPIHTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.security import APIKeyHeader
from starlette.exceptions import HTTPException

from utils.config import API_KEY, STATIC_RESPONSE
from utils.enums import HttpStatusCode
from utils.models import (
    QueryRequest,
    QueryResponse,
    HealthResponse,
    ErrorResponse,
)
from utils.pipelines import generate_hypotheses_pipeline
from utils.logging_config import setup_logging

# Setup logging
logger = setup_logging()
logger.info("Starting AI Co-Scientist application")

def save_query_response(query: str, response_data: dict):
    """Save query and response to JSON file in results/ directory."""
    try:
        results_file = "results/query_responses.json"
        
        # Load existing data if file exists
        if os.path.exists(results_file):
            with open(results_file, 'r') as f:
                data = json.load(f)
        else:
            data = []
        
        # Append new entry
        entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response_data
        }
        data.append(entry)
        
        # Save back to file
        with open(results_file, 'w') as f:
            json.dump(data, f, indent=2)
            
        logger.info(f"Saved query/response to {results_file}")
        
    except Exception as e:
        logger.error(f"Failed to save query/response: {str(e)}")

app = FastAPI(
    title="AI Co-Scientist",
    description="A multi-agent AI system for generating scientific hypotheses and research plans",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "AI Co-Scientist",
            "description": "Endpoints for AI Co-Scientist hypothesis generation",
        },
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/robots.txt", include_in_schema=False)
async def get_robots_txt():
    robots_txt_path = os.path.join("static", "robots.txt")
    return FileResponse(robots_txt_path, media_type="text/plain")

templates = Jinja2Templates(directory="static")

@app.get("/", tags=["Index"], response_class=HTMLResponse)
def index(request):
    return templates.TemplateResponse("index.html", {"request": request})

api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
)

async def get_api_key(
    api_key_header: str = Security(api_key_header),
):
    if api_key_header:
        if api_key_header == API_KEY:
            return API_KEY
        else:
            raise HTTPException(
                status_code=HttpStatusCode.UNAUTHORIZED.value,
                detail="Invalid API Key",
            )
    else:
        raise HTTPException(
            status_code=HttpStatusCode.BAD_REQUEST.value,
            detail="Please enter an API key",
        )

@app.get("/health", tags=["Health"], response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0"
    )

@app.post(
    path="/query",
    tags=["AI Co-Scientist"],
    response_model=QueryResponse,
    response_description="Successful Response",
    description="Process a scientific query and return generated hypotheses",
    name="Generate Hypotheses",
)
async def process_scientific_query(
    request: QueryRequest,
    api_key: str = Depends(get_api_key),
):
    """
    Process a scientific query and return generated hypotheses.
    
    This endpoint implements the complete AI co-scientist workflow using:
    1. Generation Agent (Gemma 3 12B) - Novel hypothesis generation
    2. Proximity Agent (Gemma 2 9B) - Knowledge retrieval and grounding
    3. Reflection Agent (OpenAI o3-mini) - Scientific critique and evaluation
    4. Ranking Agent (Gemma 2 9B) - Multi-criteria hypothesis ranking
    5. Evolution Agent (Llama 3.3 70B) - Iterative hypothesis refinement
    6. Meta-Review Agent (OpenAI o3-mini) - Final review and experimental planning
    """
    
    try:
        logger.info(f"Processing scientific query: {request.query[:100]}...")
        
        # Validate request
        if not request.query.strip():
            raise FastAPIHTTPException(
                status_code=400,
                detail="Query cannot be empty"
            )
        
        if request.max_hypotheses < 1 or request.max_hypotheses > 10:
            raise FastAPIHTTPException(
                status_code=400,
                detail="max_hypotheses must be between 1 and 10"
            )
        
        # Process through multi-agent pipeline
        response = generate_hypotheses_pipeline(request)
        
        logger.info(f"Successfully generated {len(response.hypotheses)} hypotheses in {response.total_processing_time:.2f}s")
        
        # Save query and response to JSON file
        save_query_response(request.query, response.model_dump())
        
        return response
        
    except FastAPIHTTPException:
        raise  # Re-raise FastAPI HTTP exceptions
    except Exception as e:
        logger.error(f"Error processing scientific query: {str(e)}", exc_info=True)
        raise FastAPIHTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, workers=4)
