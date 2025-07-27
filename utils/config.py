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

# Anthropic Configuration (for Claude Opus 4 orchestrator)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Tavily Search Configuration
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Model Configuration
PRIMARY_MODEL = "llama-3.3-70b-versatile"  # For complex reasoning
SECONDARY_MODEL = "gemma2-9b-it"  # For faster operations

MODEL_STRENGTHS = {
    "llama-3.3-70b": {
        "model": "Llama 3.3 70B",
        "strengths": "Large parameter model with excellent complex reasoning capabilities, strong logical deduction, high context understanding, and creative problem-solving abilities. Handles multi-step reasoning tasks effectively."
    },
    "qwen-3-32b": {
        "model": "Qwen 3 32B", 
        "strengths": "Strong mathematical and quantitative reasoning capabilities, excellent logical analysis, precise calculations, pattern recognition, and computational thinking. High performance on analytical tasks."
    },
    "gemma-3-12b": {
        "model": "Gemma 3 12B",
        "strengths": "Efficient and fast inference with optimized processing capabilities. Good balance of performance and speed, low latency responses, and resource-efficient operations."
    },
    "llama-4-scout": {
        "model": "Llama 4 Scout",
        "strengths": "Excellent exploration and discovery capabilities, creative thinking, novel approach generation, divergent reasoning, and innovative connection-making between disparate concepts."
    },
    "gpt-o3-mini": {
        "model": "GPT o3 mini",
        "strengths": "Strong coordination and orchestration capabilities, excellent task management, systematic planning, resource optimization, and multi-agent workflow handling."
    },
    "mistral-7b": {
        "model": "Mistral 7B",
        "strengths": "Focused analytical capabilities, detailed evaluation skills, critical thinking, precision in assessment, attention to detail, and thorough examination of information."
    },
    "gemini-2.5-pro": {
        "model": "Gemini 2.5 Pro",
        "strengths": "Advanced multimodal processing capabilities, visual understanding, cross-modal reasoning, integrated analysis of text and images, and comprehensive data interpretation."
    },
    "claude-opus-4": {
        "model": "Claude Opus 4",
        "strengths": "Comprehensive analysis capabilities, thorough evaluation skills, detailed synthesis, deep understanding, and high-quality reasoning across complex topics."
    },
    "deepseek-r1": {
        "model": "DeepSeek R1",
        "strengths": "Deep reasoning and reflection capabilities, metacognitive analysis, reasoning chain construction, logical verification, and self-reflective problem-solving approaches."
    }
}

origins = [
    AI_CO_SCIENTIST_API_BASE,
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
] 

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE = os.getenv("DATABASE")
REQUESTS_COLLECTION = os.getenv("REQUESTS_COLLECTION")
