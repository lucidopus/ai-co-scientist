import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("API_KEY")

# API Base URLs
AI_CO_SCIENTIST_API_BASE = os.getenv("AI_CO_SCIENTIST_API_BASE")

# Gemma Service Configuration
GEMMA_SERVICE_URL = os.getenv("GEMMA_SERVICE_URL", "https://gemma-12b-service-7arvmwsqqq-ez.a.run.app")

origins = [
    AI_CO_SCIENTIST_API_BASE,
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
] 