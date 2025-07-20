import os


API_KEY = os.getenv("API_KEY")

# API Base URLs
AI_CO_SCIENTIST_API_BASE = os.getenv("AI_CO_SCIENTIST_API_BASE")

# Gemma Service Configuration
GEMMA_SERVICE_URL = os.getenv("GEMMA_SERVICE_URL")

# GROQ Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# OpenAI Configuration (backup)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Model Configuration
PRIMARY_MODEL = "llama-3.3-70b-versatile"  # For complex reasoning
SECONDARY_MODEL = "gemma2-9b-it"  # For faster operations

origins = [
    AI_CO_SCIENTIST_API_BASE,
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
] 

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE = os.getenv("DATABASE")
REQUESTS_COLLECTION = os.getenv("REQUESTS_COLLECTION")
