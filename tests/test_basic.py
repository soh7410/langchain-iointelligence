"""Simple test without langsmith dependencies."""

from unittest.mock import Mock, patch, PropertyMock


# Skip langsmith-related tests
def test_basic_import():
    """Test that the package can be imported."""
    from langchain_iointelligence import IOIntelligenceLLM

    assert IOIntelligenceLLM is not None


def test_llm_initialization():
    """Test LLM initialization."""
    from langchain_iointelligence.llm import IOIntelligenceLLM

    llm = IOIntelligenceLLM(api_key="test_key", api_url="https://test.api.com/v1/completions")
    assert llm.io_api_key == "test_key"
    assert llm.io_api_url == "https://test.api.com/v1/completions"
    assert llm._llm_type == "io_intelligence"


def test_basic_call():
    """Test basic API call."""
    from langchain_iointelligence.llm import IOIntelligenceLLM

    llm = IOIntelligenceLLM(api_key="test_key", api_url="https://test.api.com/v1/completions")

    mock_client = Mock()
    mock_client.post_with_retry.return_value = {"choices": [{"text": "Test response"}]}

    with patch.object(type(llm), "http_client", new_callable=PropertyMock, return_value=mock_client):
        result = llm._call("Test prompt")
        assert result == "Test response"


if __name__ == "__main__":
    test_basic_import()
    test_llm_initialization()
    print("Basic tests passed!")
