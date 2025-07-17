"""Test cases for IOIntelligenceChatModel."""

import os
import pytest
from unittest.mock import Mock, patch
from langchain_core.exceptions import OutputParserException as GenerationError
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from langchain_iointelligence.chat import IOIntelligenceChatModel


class TestIOIntelligenceChatModel:
    """Test cases for IOIntelligenceChatModel class."""

    def test_init_with_env_vars(self):
        """Test initialization with environment variables."""
        with patch.dict(os.environ, {
            'IO_API_KEY': 'test_key',
            'IO_API_URL': 'https://test.api.com/v1/chat/completions'
        }):
            chat = IOIntelligenceChatModel()
            assert chat.io_api_key == 'test_key'
            assert chat.io_api_url == 'https://test.api.com/v1/chat/completions'

    def test_init_with_params(self):
        """Test initialization with explicit parameters."""
        chat = IOIntelligenceChatModel(
            api_key='param_key',
            api_url='https://param.api.com/v1/chat/completions',
            model='custom-model',
            max_tokens=2000,
            temperature=0.5,
            timeout=60,
            max_retries=5
        )
        assert chat.io_api_key == 'param_key'
        assert chat.io_api_url == 'https://param.api.com/v1/chat/completions'
        assert chat.model == 'custom-model'
        assert chat.max_tokens == 2000
        assert chat.temperature == 0.5
        assert chat.timeout == 60
        assert chat.max_retries == 5

    def test_init_missing_api_key(self):
        """Test initialization fails when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="IO_API_KEY must be provided"):
                IOIntelligenceChatModel()

    def test_llm_type(self):
        """Test _llm_type property."""
        chat = IOIntelligenceChatModel(
            api_key='test_key',
            api_url='https://test.api.com/v1/chat/completions'
        )
        assert chat._llm_type == "io_intelligence_chat"

    def test_convert_messages_to_api_format(self):
        """Test message conversion to API format."""
        chat = IOIntelligenceChatModel(
            api_key='test_key',
            api_url='https://test.api.com/v1/chat/completions'
        )
        
        messages = [
            SystemMessage(content="You are a helpful assistant"),
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there!")
        ]
        
        api_messages = chat._convert_messages_to_api_format(messages)
        
        expected = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        
        assert api_messages == expected

    @patch('langchain_iointelligence.chat.requests.post')
    def test_generate_success(self, mock_post):
        """Test successful chat generation."""
        # Mock successful response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "choices": [{
                "message": {"content": "This is a test response"},
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15
            }
        }
        mock_post.return_value = mock_response

        chat = IOIntelligenceChatModel(
            api_key='test_key',
            api_url='https://test.api.com/v1/chat/completions'
        )
        
        messages = [HumanMessage(content="Test message")]
        result = chat._generate(messages)
        
        assert len(result.generations) == 1
        generation = result.generations[0]
        assert isinstance(generation.message, AIMessage)
        assert generation.message.content == "This is a test response"
        assert generation.generation_info["finish_reason"] == "stop"
        assert generation.generation_info["usage"]["total_tokens"] == 15

        # Verify API call was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]['headers']['Authorization'] == 'Bearer test_key'
        assert 'messages' in call_args[1]['json']
        assert call_args[1]['json']['messages'][0]['content'] == 'Test message'

    @patch('langchain_iointelligence.chat.requests.post')
    def test_generate_with_stop_words(self, mock_post):
        """Test generation with stop words."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Response with stop"}}]
        }
        mock_post.return_value = mock_response

        chat = IOIntelligenceChatModel(
            api_key='test_key',
            api_url='https://test.api.com/v1/chat/completions'
        )
        
        messages = [HumanMessage(content="Test prompt")]
        result = chat._generate(messages, stop=["stop", "end"])
        
        assert result.generations[0].message.content == "Response with stop"
        
        # Verify stop words were included
        call_args = mock_post.call_args
        assert call_args[1]['json']['stop'] == ["stop", "end"]

    @patch('langchain_iointelligence.chat.requests.post')
    def test_generate_completion_format(self, mock_post):
        """Test generation with completion format response."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "choices": [{"text": "Completion format response"}]
        }
        mock_post.return_value = mock_response

        chat = IOIntelligenceChatModel(
            api_key='test_key',
            api_url='https://test.api.com/v1/chat/completions'
        )
        
        messages = [HumanMessage(content="Test message")]
        result = chat._generate(messages)
        
        assert result.generations[0].message.content == "Completion format response"

    @patch('langchain_iointelligence.chat.requests.post')
    def test_generate_request_exception(self, mock_post):
        """Test generation with request exception."""
        mock_post.side_effect = Exception("Connection error")

        chat = IOIntelligenceChatModel(
            api_key='test_key',
            api_url='https://test.api.com/v1/chat/completions'
        )
        
        messages = [HumanMessage(content="Test message")]
        
        with pytest.raises(GenerationError, match="API request failed"):
            chat._generate(messages)

    @patch('langchain_iointelligence.chat.requests.post')
    def test_generate_invalid_response(self, mock_post):
        """Test generation with invalid response format."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"invalid": "response"}
        mock_post.return_value = mock_response

        chat = IOIntelligenceChatModel(
            api_key='test_key',
            api_url='https://test.api.com/v1/chat/completions'
        )
        
        messages = [HumanMessage(content="Test message")]
        
        with pytest.raises(GenerationError, match="No choices in API response"):
            chat._generate(messages)

    def test_invoke_integration(self):
        """Test invoke method integration."""
        with patch('langchain_iointelligence.chat.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Integration test response"}}]
            }
            mock_post.return_value = mock_response

            chat = IOIntelligenceChatModel(
                api_key='test_key',
                api_url='https://test.api.com/v1/chat/completions'
            )
            
            messages = [HumanMessage(content="Test integration")]
            result = chat.invoke(messages)
            
            assert isinstance(result, AIMessage)
            assert result.content == "Integration test response"

    def test_identifying_params(self):
        """Test _identifying_params property."""
        chat = IOIntelligenceChatModel(
            api_key='test_key',
            api_url='https://test.api.com/v1/chat/completions',
            model='test-model',
            max_tokens=1500,
            temperature=0.8,
            timeout=45,
            max_retries=2
        )
        params = chat._identifying_params
        assert params['model'] == 'test-model'
        assert params['max_tokens'] == 1500
        assert params['temperature'] == 0.8
        assert params['timeout'] == 45
        assert params['max_retries'] == 2


if __name__ == "__main__":
    pytest.main([__file__])
