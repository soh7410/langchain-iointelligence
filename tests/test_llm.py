"""Test cases for IOIntelligenceLLM."""

import os
from unittest.mock import Mock, patch, PropertyMock

import pytest
from langchain_core.exceptions import OutputParserException as GenerationError

from langchain_iointelligence.llm import IOIntelligenceLLM
from langchain_iointelligence.exceptions import IOIntelligenceConnectionError


class TestIOIntelligenceLLM:
    """Test cases for IOIntelligenceLLM class."""

    def test_init_with_env_vars(self):
        """Test initialization with environment variables."""
        with patch.dict(
            os.environ,
            {
                "IO_API_KEY": "test_key",
                "IO_API_URL": "https://test.api.com/v1/chat/completions"
            },
        ):
            llm = IOIntelligenceLLM()
            assert llm.io_api_key == "test_key"
            assert llm.io_api_url == "https://test.api.com/v1/chat/completions"

    def test_init_with_params(self):
        """Test initialization with explicit parameters."""
        llm = IOIntelligenceLLM(
            api_key="param_key",
            api_url="https://param.api.com/v1/chat/completions",
            model="custom-model",
            max_tokens=2000,
            temperature=0.5,
        )
        assert llm.io_api_key == "param_key"
        assert llm.io_api_url == "https://param.api.com/v1/chat/completions"
        assert llm.model == "custom-model"
        assert llm.max_tokens == 2000
        assert llm.temperature == 0.5

    def test_init_missing_api_key(self):
        """Test initialization fails when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(
                ValueError, match="IO_API_KEY must be provided"
            ):
                IOIntelligenceLLM()

    def test_init_missing_api_url(self):
        """Test initialization fails when API URL is missing."""
        with patch.dict(os.environ, {"IO_API_KEY": "test_key"}, clear=True):
            with pytest.raises(
                ValueError, match="IO_API_URL must be provided"
            ):
                IOIntelligenceLLM()

    def test_llm_type(self):
        """Test _llm_type property."""
        llm = IOIntelligenceLLM(
            api_key="test_key",
            api_url="https://test.api.com/v1/chat/completions"
        )
        assert llm._llm_type == "io_intelligence"

    def test_identifying_params(self):
        """Test _identifying_params property."""
        llm = IOIntelligenceLLM(
            api_key="test_key",
            api_url="https://test.api.com/v1/chat/completions",
            model="test-model",
            max_tokens=1500,
            temperature=0.8,
        )
        params = llm._identifying_params
        assert params["model"] == "test-model"
        assert params["max_tokens"] == 1500
        assert params["temperature"] == 0.8

    def test_call_success(self):
        """Test successful API call."""
        llm = IOIntelligenceLLM(
            api_key="test_key",
            api_url="https://test.api.com/v1/chat/completions"
        )

        mock_client = Mock()
        mock_client.post_with_retry.return_value = {
            "choices": [{"message": {"content": "This is a test response"}}]
        }

        with patch.object(type(llm), "http_client", new_callable=PropertyMock, return_value=mock_client):
            result = llm._call("Test prompt")
            assert result == "This is a test response"

            # Verify request payload
            mock_client.post_with_retry.assert_called_once()
            request_data = mock_client.post_with_retry.call_args[0][0]
            assert "messages" in request_data
            assert request_data["messages"][0]["content"] == "Test prompt"
            assert request_data["model"] == "meta-llama/Llama-3.3-70B-Instruct"
            assert request_data["max_tokens"] == 1000
            assert request_data["temperature"] == 0.7

    def test_call_with_stop_words(self):
        """Test API call with stop words."""
        llm = IOIntelligenceLLM(
            api_key="test_key",
            api_url="https://test.api.com/v1/chat/completions"
        )

        mock_client = Mock()
        mock_client.post_with_retry.return_value = {
            "choices": [{"message": {"content": "Response with stop"}}]
        }

        with patch.object(type(llm), "http_client", new_callable=PropertyMock, return_value=mock_client):
            result = llm._call("Test prompt", stop=["stop", "end"])
            assert result == "Response with stop"

            # Verify stop words were included
            request_data = mock_client.post_with_retry.call_args[0][0]
            assert request_data["stop"] == ["stop", "end"]

    def test_call_request_exception(self):
        """Test API call with connection exception propagates as IOIntelligenceConnectionError."""
        llm = IOIntelligenceLLM(
            api_key="test_key",
            api_url="https://test.api.com/v1/chat/completions"
        )

        mock_client = Mock()
        mock_client.post_with_retry.side_effect = IOIntelligenceConnectionError("Connection error")

        with patch.object(type(llm), "http_client", new_callable=PropertyMock, return_value=mock_client):
            with pytest.raises(IOIntelligenceConnectionError):
                llm._call("Test prompt")

    def test_call_request_exception_caught_as_generation_error(self):
        """Test backward compat: IOIntelligenceConnectionError is catchable as GenerationError."""
        llm = IOIntelligenceLLM(
            api_key="test_key",
            api_url="https://test.api.com/v1/chat/completions"
        )

        mock_client = Mock()
        mock_client.post_with_retry.side_effect = IOIntelligenceConnectionError("Connection error")

        with patch.object(type(llm), "http_client", new_callable=PropertyMock, return_value=mock_client):
            with pytest.raises(GenerationError):
                llm._call("Test prompt")

    def test_call_invalid_response_format(self):
        """Test API call with invalid response format."""
        llm = IOIntelligenceLLM(
            api_key="test_key",
            api_url="https://test.api.com/v1/chat/completions"
        )

        mock_client = Mock()
        mock_client.post_with_retry.return_value = {"invalid": "response"}

        with patch.object(type(llm), "http_client", new_callable=PropertyMock, return_value=mock_client):
            with pytest.raises(
                GenerationError, match="No choices in API response"
            ):
                llm._call("Test prompt")

    def test_call_empty_choices(self):
        """Test API call with empty choices."""
        llm = IOIntelligenceLLM(
            api_key="test_key",
            api_url="https://test.api.com/v1/chat/completions"
        )

        mock_client = Mock()
        mock_client.post_with_retry.return_value = {"choices": []}

        with patch.object(type(llm), "http_client", new_callable=PropertyMock, return_value=mock_client):
            with pytest.raises(
                GenerationError, match="No choices in API response"
            ):
                llm._call("Test prompt")

    def test_integration_example(self):
        """Test integration with LangChain components (mock)."""
        llm = IOIntelligenceLLM(
            api_key="test_key",
            api_url="https://test.api.com/v1/chat/completions"
        )

        mock_client = Mock()
        mock_client.post_with_retry.return_value = {
            "choices": [
                {"message": {"content": "Integration test response"}}
            ]
        }

        with patch.object(type(llm), "http_client", new_callable=PropertyMock, return_value=mock_client):
            # Test direct call (using invoke instead of deprecated __call__)
            result = llm.invoke("Test integration prompt")
            assert result == "Integration test response"

    @patch.dict(
        os.environ,
        {
            "IO_API_KEY": "env_test_key",
            "IO_API_URL": "https://env.test.api.com/v1/chat/completions",
        },
    )
    def test_env_loading_integration(self):
        """Test that environment variables are loaded correctly."""
        llm = IOIntelligenceLLM()

        mock_client = Mock()
        mock_client.post_with_retry.return_value = {
            "choices": [{"message": {"content": "Env test response"}}]
        }

        with patch.object(type(llm), "http_client", new_callable=PropertyMock, return_value=mock_client):
            result = llm.invoke("Test env prompt")
            assert result == "Env test response"

            # Verify correct API URL was set on the LLM instance
            assert llm.io_api_url == "https://env.test.api.com/v1/chat/completions"

    def test_retry_params_and_identifying_params(self):
        """Test that retry/timeout fields are stored and _identifying_params preserves legacy keys."""
        llm = IOIntelligenceLLM(
            api_key="test_key",
            api_url="https://test.api.com/v1/chat/completions",
            max_retries=5,
            timeout=60,
        )
        assert llm.max_retries == 5
        assert llm.timeout == 60
        # Legacy keys must be present
        params = llm._identifying_params
        assert "model" in params
        assert "max_tokens" in params
        assert "temperature" in params

    def test_http_client_instance_params(self):
        """Test that http_client is lazily created with the correct parameters."""
        from langchain_iointelligence.http_client import IOIntelligenceHTTPClient

        llm = IOIntelligenceLLM(
            api_key="mykey",
            api_url="https://api.example.com/v1/chat/completions",
            timeout=45,
            max_retries=2,
            retry_delay=0.5,
        )
        client = llm.http_client
        assert isinstance(client, IOIntelligenceHTTPClient)
        assert client.api_key == "mykey"
        assert client.api_url == "https://api.example.com/v1/chat/completions"
        assert client.timeout == 45
        assert client.max_retries == 2
        assert client.retry_delay == 0.5


if __name__ == "__main__":
    pytest.main([__file__])
