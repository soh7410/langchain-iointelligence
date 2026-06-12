"""Tests for tool/function calling and structured output."""

from unittest.mock import Mock, PropertyMock, patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from pydantic import BaseModel, Field

from langchain_iointelligence.chat import (IOIntelligenceChatModel,
                                           _convert_message_to_dict,
                                           _format_tool_choice,
                                           _lc_tool_call_to_openai,
                                           _parse_response_tool_calls)


def _model():
    return IOIntelligenceChatModel(
        api_key="k", api_url="https://test.api.com/v1/chat/completions"
    )


class GetWeather(BaseModel):
    """Get the current weather in a location."""

    location: str = Field(..., description="City name")


def _tool_call_response(name="GetWeather", args='{"location": "Tokyo"}'):
    return {
        "id": "resp-1",
        "model": "m",
        "choices": [
            {
                "finish_reason": "tool_calls",
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_abc",
                            "type": "function",
                            "function": {"name": name, "arguments": args},
                        }
                    ],
                },
            }
        ],
        "usage": {"prompt_tokens": 5, "completion_tokens": 7, "total_tokens": 12},
    }


class TestMessageConversion:
    def test_tool_message_role(self):
        d = _convert_message_to_dict(
            ToolMessage(content="22C", tool_call_id="call_abc")
        )
        assert d == {"role": "tool", "content": "22C", "tool_call_id": "call_abc"}

    def test_ai_message_with_tool_calls(self):
        msg = AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "GetWeather",
                    "args": {"location": "Tokyo"},
                    "id": "call_abc",
                    "type": "tool_call",
                }
            ],
        )
        d = _convert_message_to_dict(msg)
        assert d["role"] == "assistant"
        assert d["content"] is None
        assert d["tool_calls"][0]["function"]["name"] == "GetWeather"
        # arguments must be a JSON string
        assert d["tool_calls"][0]["function"]["arguments"] == '{"location": "Tokyo"}'

    def test_lc_tool_call_to_openai(self):
        out = _lc_tool_call_to_openai(
            {"name": "f", "args": {"x": 1}, "id": "id1"}
        )
        assert out["type"] == "function"
        assert out["id"] == "id1"
        assert out["function"]["arguments"] == '{"x": 1}'


class TestToolChoiceFormatting:
    @pytest.mark.parametrize(
        "value,expected",
        [
            (True, "required"),
            (False, "none"),
            ("auto", "auto"),
            ("none", "none"),
            ("required", "required"),
            ("any", "required"),
        ],
    )
    def test_keywords(self, value, expected):
        assert _format_tool_choice(value, ["GetWeather"]) == expected

    def test_named_tool(self):
        assert _format_tool_choice("GetWeather", ["GetWeather"]) == {
            "type": "function",
            "function": {"name": "GetWeather"},
        }

    def test_passthrough_dict(self):
        d = {"type": "function", "function": {"name": "x"}}
        assert _format_tool_choice(d, []) is d


class TestParseResponseToolCalls:
    def test_valid(self):
        valid, invalid = _parse_response_tool_calls(
            {
                "tool_calls": [
                    {
                        "id": "c1",
                        "type": "function",
                        "function": {"name": "GetWeather", "arguments": '{"location": "Tokyo"}'},
                    }
                ]
            }
        )
        assert not invalid
        assert valid[0]["name"] == "GetWeather"
        assert valid[0]["args"] == {"location": "Tokyo"}
        assert valid[0]["id"] == "c1"

    def test_invalid_arguments(self):
        valid, invalid = _parse_response_tool_calls(
            {
                "tool_calls": [
                    {
                        "id": "c1",
                        "type": "function",
                        "function": {"name": "GetWeather", "arguments": "{not json"},
                    }
                ]
            }
        )
        assert not valid
        assert invalid and invalid[0]["type"] == "invalid_tool_call"


class TestBindTools:
    def test_bind_tools_sends_schema_and_choice(self):
        chat = _model()
        bound = chat.bind_tools([GetWeather], tool_choice="GetWeather")
        kwargs = bound.kwargs
        assert kwargs["tools"][0]["function"]["name"] == "GetWeather"
        assert kwargs["tool_choice"] == {
            "type": "function",
            "function": {"name": "GetWeather"},
        }

    def test_invoke_parses_tool_calls(self):
        chat = _model()
        mock_client = Mock()
        mock_client.post_with_retry.return_value = _tool_call_response()
        with patch.object(type(chat), "http_client", new_callable=PropertyMock, return_value=mock_client):
            result = chat.bind_tools([GetWeather]).invoke(
                [HumanMessage(content="weather in Tokyo?")]
            )
        assert isinstance(result, AIMessage)
        assert result.tool_calls
        assert result.tool_calls[0]["name"] == "GetWeather"
        assert result.tool_calls[0]["args"] == {"location": "Tokyo"}
        assert result.usage_metadata["total_tokens"] == 12


class TestStructuredOutput:
    def test_function_calling_pydantic(self):
        chat = _model()
        runnable = chat.with_structured_output(GetWeather)
        mock_client = Mock()
        mock_client.post_with_retry.return_value = _tool_call_response()
        with patch.object(type(chat), "http_client", new_callable=PropertyMock, return_value=mock_client):
            out = runnable.invoke([HumanMessage(content="weather in Tokyo?")])
        assert isinstance(out, GetWeather)
        assert out.location == "Tokyo"

    def test_function_calling_sets_response_tool_choice(self):
        chat = _model()
        # The bound runnable should force the tool.
        runnable = chat.with_structured_output(GetWeather)
        # First step of the chain is the bound LLM.
        bound = runnable.steps[0] if hasattr(runnable, "steps") else runnable.first
        assert bound.kwargs["tool_choice"]["function"]["name"] == "GetWeather"

    def test_json_schema_sets_response_format(self):
        chat = _model()
        runnable = chat.with_structured_output(GetWeather, method="json_schema")
        bound = runnable.first
        rf = bound.kwargs["response_format"]
        assert rf["type"] == "json_schema"
        assert rf["json_schema"]["name"] == "GetWeather"
        assert "location" in rf["json_schema"]["schema"]["properties"]

    def test_json_mode_sets_response_format(self):
        chat = _model()
        runnable = chat.with_structured_output(GetWeather, method="json_mode")
        bound = runnable.first
        assert bound.kwargs["response_format"] == {"type": "json_object"}

    def test_invalid_method(self):
        chat = _model()
        with pytest.raises(ValueError, match="Unsupported method"):
            chat.with_structured_output(GetWeather, method="nope")

    def test_json_schema_parses_content(self):
        chat = _model()
        json_resp = {
            "id": "1",
            "model": "m",
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"role": "assistant", "content": '{"location": "Tokyo"}'},
                }
            ],
            "usage": {},
        }
        runnable = chat.with_structured_output(GetWeather, method="json_schema")
        mock_client = Mock()
        mock_client.post_with_retry.return_value = json_resp
        with patch.object(type(chat), "http_client", new_callable=PropertyMock, return_value=mock_client):
            out = runnable.invoke([HumanMessage(content="x")])
        assert isinstance(out, GetWeather)
        assert out.location == "Tokyo"

    def test_include_raw(self):
        chat = _model()
        runnable = chat.with_structured_output(GetWeather, include_raw=True)
        mock_client = Mock()
        mock_client.post_with_retry.return_value = _tool_call_response()
        with patch.object(type(chat), "http_client", new_callable=PropertyMock, return_value=mock_client):
            out = runnable.invoke([HumanMessage(content="x")])
        assert set(out.keys()) == {"raw", "parsed", "parsing_error"}
        assert isinstance(out["parsed"], GetWeather)
        assert out["parsing_error"] is None


class TestMultiTurnRoundTrip:
    def test_tool_conversation_roundtrips(self):
        chat = _model()
        messages = [
            HumanMessage(content="weather?"),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "GetWeather",
                        "args": {"location": "Tokyo"},
                        "id": "c1",
                        "type": "tool_call",
                    }
                ],
            ),
            ToolMessage(content="22C", tool_call_id="c1"),
        ]
        api = chat._convert_messages_to_api_format(messages)
        assert [m["role"] for m in api] == ["user", "assistant", "tool"]
        assert api[1]["tool_calls"][0]["function"]["name"] == "GetWeather"
        assert api[2]["tool_call_id"] == "c1"


class TestStreamingToolCalls:
    def test_tool_call_chunks_accumulate(self):
        from langchain_iointelligence.streaming import IOIntelligenceStreamer

        streamer = IOIntelligenceStreamer("k", "https://x")
        deltas = [
            {"choices": [{"delta": {"tool_calls": [
                {"index": 0, "id": "c1", "function": {"name": "GetWeather", "arguments": ""}}]}}]},
            {"choices": [{"delta": {"tool_calls": [
                {"index": 0, "function": {"arguments": '{"location":'}}]}}]},
            {"choices": [{"delta": {"tool_calls": [
                {"index": 0, "function": {"arguments": '"Tokyo"}'}}]}}]},
        ]
        chunks = [streamer._create_chat_chunk(d) for d in deltas]
        merged = chunks[0]
        for chunk in chunks[1:]:
            merged = merged + chunk
        assert merged.message.tool_calls[0]["name"] == "GetWeather"
        assert merged.message.tool_calls[0]["args"] == {"location": "Tokyo"}
