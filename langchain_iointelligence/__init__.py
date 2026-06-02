"""LangChain wrapper for io Intelligence LLM API."""

from .chat import IOIntelligenceChat, IOIntelligenceChatModel
from .exceptions import (IOIntelligenceAPIError,
                         IOIntelligenceAuthenticationError,
                         IOIntelligenceConnectionError, IOIntelligenceError,
                         IOIntelligenceInvalidResponseError,
                         IOIntelligenceRateLimitError,
                         IOIntelligenceServerError, IOIntelligenceTimeoutError)
from .llm import IOIntelligenceLLM
from .utils import (IOIntelligenceUtils, is_model_available,
                    list_available_models)
from .vision import (DEFAULT_VISION_MODEL, MAX_IMAGES_PER_REQUEST,
                     VISION_MODELS, encode_image_to_data_url,
                     image_content_block, vision_message)

__version__ = "0.4.0"
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
    "is_model_available",
    # Vision / multimodal helpers
    "vision_message",
    "image_content_block",
    "encode_image_to_data_url",
    "VISION_MODELS",
    "DEFAULT_VISION_MODEL",
    "MAX_IMAGES_PER_REQUEST",
]
