import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("API_KEY")

# API Base URLs
AI_CO_SCIENTIST_API_BASE = os.getenv("AI_CO_SCIENTIST_API_BASE")

origins = [
    AI_CO_SCIENTIST_API_BASE,
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
] 