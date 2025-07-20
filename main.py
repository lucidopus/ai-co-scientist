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

from utils.config import API_KEY
from utils.enums import HttpStatusCode
from utils.models import (
    QueryRequest,
    QueryResponse,
    SampleQueryResponse,
    HealthResponse,
    ErrorResponse,
)
from utils.pipelines import generate_hypotheses_pipeline
from utils.logging_config import setup_logging
from utils.database import requests_collection
from utils.helper import generate_sample_query
from utils.terminal_colors import (
    print_header, print_step, print_info, print_success, 
    print_error, print_warning, colored_print, Colors
)


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Setup logging
logger = setup_logging()
logger.info("Starting AI Co-Scientist application")

print_header("🔬 AI CO-SCIENTIST SYSTEM INITIALIZING")
print_step("Application Bootstrap", "STARTING")
print_info("Multi-agent AI system for scientific hypothesis generation")
print_step("Application Bootstrap", "COMPLETED")

def save_query_response(query: str, response_data: dict):
    """Save query and response to JSON file and MongoDB collection."""
    print_info("Saving query response to file and database")
    try:
        # Save to JSON file (existing functionality)
        results_file = "results/query_responses.json"
        
        # Load existing data if file exists and is not empty
        data = []
        if os.path.exists(results_file) and os.path.getsize(results_file) > 0:
            try:
                with open(results_file, 'r') as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                # If file is corrupted or empty, start with empty list
                logger.warning(f"Corrupted or empty JSON file {results_file}, starting fresh")
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
            json.dump(data, f, indent=2, cls=DateTimeEncoder)
            
        logger.info(f"Saved query/response to {results_file}")
        print_success(f"Saved to JSON file: {results_file}")
        
        # Save to MongoDB
        print_info("Saving to MongoDB database")
        try:
            mongo_entry = {
                "timestamp": datetime.now(),
                "query": query,
                "response": response_data,
                "created_at": datetime.now().isoformat()
            }
            result = requests_collection.insert_one(mongo_entry)
            logger.info(f"Saved query/response to MongoDB with ID: {result.inserted_id}")
            print_success(f"Saved to MongoDB with ID: {result.inserted_id}")
        except Exception as mongo_error:
            logger.error(f"Failed to save to MongoDB: {str(mongo_error)}")
            print_error(f"MongoDB save failed: {str(mongo_error)}")
        
    except Exception as e:
        logger.error(f"Failed to save query/response: {str(e)}")
        print_error(f"Save operation failed: {str(e)}")

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
        print_header("🚀 PROCESSING SCIENTIFIC QUERY")
        print_step("Query Processing", "STARTING")
        print_info(f"Query: {request.query[:100]}{'...' if len(request.query) > 100 else ''}")
        logger.info(f"Processing scientific query: {request.query[:100]}...")
        
        # Validate request
        print_step("Input Validation", "RUNNING")
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
        
        print_step("Input Validation", "COMPLETED")
        print_success("Input validation passed successfully")
        
        # Process through multi-agent pipeline
        print_step("Multi-Agent Pipeline", "STARTING")
        print_info("Engaging 6-agent collaboration system")
        response = generate_hypotheses_pipeline(request)
 
        logger.info(f"Successfully generated {len(response.hypotheses)} hypotheses in {response.total_processing_time:.2f}s")
        
        print_step("Multi-Agent Pipeline", "COMPLETED")
        print_success(f"Generated {len(response.hypotheses)} hypotheses in {response.total_processing_time:.2f}s")
        
        # Save query and response to JSON file
        print_step("Data Persistence", "RUNNING")
        save_query_response(request.query, response.model_dump())
        print_step("Data Persistence", "COMPLETED")
        
        print_header("✅ QUERY PROCESSING COMPLETE")
        print_success("Scientific hypotheses generated and saved")
        
        return response
        
    except FastAPIHTTPException:
        raise  # Re-raise FastAPI HTTP exceptions
    except Exception as e:
        print_step("Query Processing", "FAILED")
        print_error(f"Error processing scientific query: {str(e)}")
        logger.error(f"Error processing scientific query: {str(e)}", exc_info=True)
        raise FastAPIHTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


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
        generated_query = generate_sample_query()
        
        # Create response object
        response = SampleQueryResponse(
            generated_query=generated_query
        )
        
        logger.info(f"Successfully generated sample query")
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating sample query: {str(e)}")
        raise FastAPIHTTPException(
            status_code=500,
            detail=f"Failed to generate sample query: {str(e)}"
        )


if __name__ == "__main__":
    print_header("🌟 STARTING AI CO-SCIENTIST SERVER")
    print_step("Server Configuration", "RUNNING")
    print_info("Host: 0.0.0.0")
    print_info("Port: 8000")
    print_info("Reload: True")
    print_info("Workers: 4")
    print_step("Server Configuration", "COMPLETED")
    print_success("Server starting up...")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, workers=4)
