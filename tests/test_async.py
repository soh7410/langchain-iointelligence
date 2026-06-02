"""Tests for native async support and streaming usage metadata."""

import asyncio

from unittest.mock import AsyncMock, patch

from langchain_core.messages import AIMessage, HumanMessage

from langchain_iointelligence.async_http_client import \
    IOIntelligenceAsyncHTTPClient
from langchain_iointelligence.chat import IOIntelligenceChatModel
from langchain_iointelligence.streaming import build_generation_chunk


def _model():
    return IOIntelligenceChatModel(
        api_key="k", api_url="https://test.api.com/v1/chat/completions"
    )


def _chat_response(content="Hello!"):
    return {
        "id": "r1",
        "model": "m",
        "choices": [
            {"finish_reason": "stop", "message": {"role": "assistant", "content": content}}
        ],
        "usage": {"prompt_tokens": 3, "completion_tokens": 2, "total_tokens": 5},
    }


async def _aiter(items):
    for item in items:
        yield item


class TestRequestData:
    def test_stream_options_added_for_streaming(self):
        chat = _model()
        data = chat._build_request_data([HumanMessage(content="hi")], None, stream=True)
        assert data["stream"] is True
        assert data["stream_options"] == {"include_usage": True}

    def test_no_stream_options_for_sync(self):
        chat = _model()
        data = chat._build_request_data([HumanMessage(content="hi")], None)
        assert "stream" not in data
        assert "stream_options" not in data

    def test_caller_can_override_stream_options(self):
        chat = _model()
        data = chat._build_request_data(
            [HumanMessage(content="hi")], None, stream=True,
            stream_options={"include_usage": False},
        )
        assert data["stream_options"] == {"include_usage": False}


class TestAsyncGenerate:
    def test_agenerate_parses_response(self):
        chat = _model()
        mock_client = AsyncMock()
        mock_client.apost_with_retry.return_value = _chat_response("Hi async")
        with patch.object(
            IOIntelligenceChatModel, "async_http_client", mock_client
        ):
            result = asyncio.run(
                chat._agenerate([HumanMessage(content="hello")])
            )
        msg = result.generations[0].message
        assert isinstance(msg, AIMessage)
        assert msg.content == "Hi async"
        assert msg.usage_metadata["total_tokens"] == 5
        mock_client.apost_with_retry.assert_awaited_once()

    def test_ainvoke_end_to_end(self):
        chat = _model()
        mock_client = AsyncMock()
        mock_client.apost_with_retry.return_value = _chat_response("pong")
        with patch.object(
            IOIntelligenceChatModel, "async_http_client", mock_client
        ):
            out = asyncio.run(chat.ainvoke("ping"))
        assert out.content == "pong"


class TestAsyncStream:
    def test_astream_yields_content_and_usage(self):
        chat = _model()
        raw_chunks = [
            {"choices": [{"delta": {"content": "Hel"}}]},
            {"choices": [{"delta": {"content": "lo"}}]},
            {"choices": [], "usage": {"prompt_tokens": 1, "completion_tokens": 2, "total_tokens": 3}},
        ]

        mock_client = AsyncMock()
        # astream is an async generator, not a coroutine.
        mock_client.astream = lambda data: _aiter(raw_chunks)

        async def _collect():
            chunks = []
            async for c in chat._astream([HumanMessage(content="hi")]):
                chunks.append(c)
            return chunks

        with patch.object(
            IOIntelligenceChatModel, "async_http_client", mock_client
        ):
            chunks = asyncio.run(_collect())

        text = "".join(c.message.content for c in chunks)
        assert text == "Hello"
        # Final chunk carries usage metadata.
        usage_chunks = [c for c in chunks if c.message.usage_metadata]
        assert usage_chunks
        assert usage_chunks[-1].message.usage_metadata["total_tokens"] == 3


class TestStreamingUsageChunk:
    def test_usage_only_chunk(self):
        chunk = build_generation_chunk(
            {"usage": {"prompt_tokens": 4, "completion_tokens": 6, "total_tokens": 10}, "choices": []}
        )
        assert chunk is not None
        assert chunk.message.usage_metadata["input_tokens"] == 4
        assert chunk.message.usage_metadata["total_tokens"] == 10

    def test_empty_chunk_without_usage_is_none(self):
        assert build_generation_chunk({"choices": []}) is None


class TestAsyncHTTPClient:
    def _patch_httpx(self, responses):
        """Patch httpx.AsyncClient to return queued fake responses for post()."""

        class _Resp:
            def __init__(self, status_code, json_data=None, text=""):
                self.status_code = status_code
                self._json = json_data
                self.text = text

            def json(self):
                return self._json

        queue = list(responses)

        class _FakeClient:
            def __init__(self, *a, **k):
                pass

            async def __aenter__(self):
                return self

            async def __aexit__(self, *a):
                return False

            async def post(self, url, headers=None, json=None):
                return queue.pop(0)

        import langchain_iointelligence.async_http_client as mod

        return patch.object(mod.httpx, "AsyncClient", _FakeClient), _Resp

    def test_success(self):
        patcher, Resp = self._patch_httpx([])
        # Build response objects after we have Resp.
        responses = [Resp(200, {"ok": True})]
        patcher, Resp = self._patch_httpx(responses)
        client = IOIntelligenceAsyncHTTPClient("k", "https://x", max_retries=0)
        with patcher:
            out = asyncio.run(client.apost_with_retry({"a": 1}))
        assert out == {"ok": True}

    def test_retries_on_server_error_then_succeeds(self):
        _, Resp = self._patch_httpx([])
        responses = [Resp(500, None, "boom"), Resp(200, {"ok": 1})]
        patcher, _ = self._patch_httpx(responses)
        client = IOIntelligenceAsyncHTTPClient(
            "k", "https://x", max_retries=2, retry_delay=0
        )
        with patcher:
            out = asyncio.run(client.apost_with_retry({"a": 1}))
        assert out == {"ok": 1}

    def test_auth_error_not_retried(self):
        from langchain_iointelligence.exceptions import \
            IOIntelligenceAuthenticationError

        _, Resp = self._patch_httpx([])
        responses = [Resp(401, None, "nope")]
        patcher, _ = self._patch_httpx(responses)
        client = IOIntelligenceAsyncHTTPClient(
            "k", "https://x", max_retries=3, retry_delay=0
        )
        with patcher:
            try:
                asyncio.run(client.apost_with_retry({"a": 1}))
                assert False, "expected auth error"
            except IOIntelligenceAuthenticationError:
                pass
