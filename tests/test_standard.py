"""LangChain standard compliance tests (unit-level, no network).

Runs the official ``langchain_tests`` ``ChatModelUnitTests`` suite against
``IOIntelligenceChatModel`` to verify the integration conforms to LangChain's
contract (init, standard params, tool binding, structured output, etc.).
"""

from typing import Tuple, Type

import pytest

from langchain_iointelligence.chat import IOIntelligenceChatModel

try:
    from langchain_tests.unit_tests import ChatModelUnitTests
except ImportError:  # pragma: no cover - dev dependency may be absent
    ChatModelUnitTests = None


@pytest.mark.skipif(
    ChatModelUnitTests is None, reason="langchain-tests is not installed"
)
class TestIOIntelligenceStandard(ChatModelUnitTests or object):
    """Standard LangChain unit-test suite for the chat model."""

    @property
    def chat_model_class(self) -> Type[IOIntelligenceChatModel]:
        return IOIntelligenceChatModel

    @property
    def chat_model_params(self) -> dict:
        return {
            "api_key": "test_key",
            "api_url": "https://test.api.com/v1/chat/completions",
            "model": "meta-llama/Llama-3.3-70B-Instruct",
        }

    @property
    def init_from_env_params(self) -> Tuple[dict, dict, dict]:
        """(env vars, init kwargs, expected attributes) for env-based init."""
        return (
            {
                "IO_API_KEY": "env_key",
                "IO_API_URL": "https://env.api.com/v1/chat/completions",
            },
            {},
            {
                "io_api_key": "env_key",
                "io_api_url": "https://env.api.com/v1/chat/completions",
            },
        )

    @property
    def has_tool_calling(self) -> bool:
        return True

    @property
    def has_structured_output(self) -> bool:
        return True

    @property
    def returns_usage_metadata(self) -> bool:
        return True

    @property
    def supports_json_mode(self) -> bool:
        return True
