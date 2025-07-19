import os

import uvicorn
from fastapi import FastAPI, Security, Depends
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
    HealthResponse,
)
from utils.pipelines import generate_hypotheses_pipeline

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
    
    This endpoint simulates the multi-agent AI co-scientist system that:
    1. Generates novel scientific hypotheses
    2. Critiques and refines them
    3. Ranks them by novelty and feasibility
    4. Provides experimental plans
    """
    
    return generate_hypotheses_pipeline(request)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, workers=4)
