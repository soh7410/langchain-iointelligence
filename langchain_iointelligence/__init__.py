"""LangChain wrapper for io Intelligence LLM API."""

from .llm import IOIntelligenceLLM
from .chat import IOIntelligenceChatModel, IOIntelligenceChat
from .exceptions import (
    IOIntelligenceError,
    IOIntelligenceAPIError,
    IOIntelligenceRateLimitError,
    IOIntelligenceServerError,
    IOIntelligenceAuthenticationError,
    IOIntelligenceTimeoutError,
    IOIntelligenceConnectionError,
    IOIntelligenceInvalidResponseError
)
from .utils import IOIntelligenceUtils, list_available_models, is_model_available

__version__ = "0.2.0"
__all__ = [
    "IOIntelligenceLLM", 
    "IOIntelligenceChatModel", 
    "IOIntelligenceChat",
    "IOIntelligenceError",
    "IOIntelligenceAPIError", 
    "IOIntelligenceRateLimitError",
    "IOIntelligenceServerError",
    "IOIntelligenceAuthenticationError",
    "IOIntelligenceTimeoutError",
    "IOIntelligenceConnectionError",
    "IOIntelligenceInvalidResponseError",
    "IOIntelligenceUtils",
    "list_available_models",
    "is_model_available"
]
