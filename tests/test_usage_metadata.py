"""Test usage metadata mapping functionality."""

from unittest.mock import Mock, PropertyMock, patch

import pytest
from langchain_core.messages import HumanMessage

from langchain_iointelligence.chat import IOIntelligenceChatModel


class TestUsageMetadata:
    """Test usage metadata mapping."""

    def test_usage_metadata_mapping(self):
        """Test that usage data is correctly mapped to LangChain standard format."""
        chat = IOIntelligenceChatModel(
            api_key="test_key",
            api_url="https://test.api.com/v1/chat/completions"
        )

        mock_client = Mock()
        mock_client.post_with_retry.return_value = {
            "choices": [
                {"message": {"content": "Test response"}, "finish_reason": "stop"}
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }

        with patch.object(type(chat), 'http_client', new_callable=PropertyMock) as mock_http_client:
            mock_http_client.return_value = mock_client
            
            messages = [HumanMessage(content="Test message")]
            result = chat._generate(messages)

            # Check that usage metadata is correctly mapped
            assert "token_usage" in result.llm_output
            usage = result.llm_output["token_usage"]
            
            assert usage["input_tokens"] == 10
            assert usage["output_tokens"] == 20
            assert usage["total_tokens"] == 30

    def test_usage_metadata_partial_data(self):
        """Test usage metadata mapping with partial data."""
        chat = IOIntelligenceChatModel(
            api_key="test_key",
            api_url="https://test.api.com/v1/chat/completions"
        )

        mock_client = Mock()
        mock_client.post_with_retry.return_value = {
            "choices": [
                {"message": {"content": "Test response"}}
            ],
            "usage": {
                "total_tokens": 30
                # Missing prompt_tokens and completion_tokens
            }
        }

        with patch.object(type(chat), 'http_client', new_callable=PropertyMock) as mock_http_client:
            mock_http_client.return_value = mock_client
            
            messages = [HumanMessage(content="Test message")]
            result = chat._generate(messages)

            # Check that only available usage data is mapped
            usage = result.llm_output["token_usage"]
            assert usage["total_tokens"] == 30
            assert "input_tokens" not in usage
            assert "output_tokens" not in usage

    def test_usage_metadata_no_usage_data(self):
        """Test usage metadata when no usage data is provided."""
        chat = IOIntelligenceChatModel(
            api_key="test_key",
            api_url="https://test.api.com/v1/chat/completions"
        )

        mock_client = Mock()
        mock_client.post_with_retry.return_value = {
            "choices": [
                {"message": {"content": "Test response"}}
            ]
            # No usage field
        }

        with patch.object(type(chat), 'http_client', new_callable=PropertyMock) as mock_http_client:
            mock_http_client.return_value = mock_client
            
            messages = [HumanMessage(content="Test message")]
            result = chat._generate(messages)

            # Check that token_usage is empty when no usage data
            usage = result.llm_output["token_usage"]
            assert usage == {}


if __name__ == "__main__":
    pytest.main([__file__])
