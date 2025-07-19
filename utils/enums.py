from enum import Enum


class HttpStatusCode(int, Enum):
    OK = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentType(str, Enum):
    GENERATION = "generation_agent"
    REFLECTION = "reflection_agent"
    RANKING = "ranking_agent" 