"""Tests for native async support and streaming usage metadata."""

import asyncio

from unittest.mock import AsyncMock, MagicMock, patch

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

        # Counter so tests can detect how many instances were created.
        _FakeClient_instances = []

        class _FakeClient:
            is_closed = False

            def __init__(self, *a, **k):
                _FakeClient_instances.append(self)

            async def aclose(self):
                pass

            async def post(self, url, headers=None, json=None):
                return queue.pop(0)

        import langchain_iointelligence.async_http_client as mod

        return (
            patch.object(mod.httpx, "AsyncClient", _FakeClient),
            _Resp,
            _FakeClient_instances,
        )

    def test_success(self):
        _, Resp, _ = self._patch_httpx([])
        # Build response objects after we have Resp.
        responses = [Resp(200, {"ok": True})]
        patcher, Resp, _ = self._patch_httpx(responses)
        client = IOIntelligenceAsyncHTTPClient("k", "https://x", max_retries=0)
        with patcher:
            out = asyncio.run(client.apost_with_retry({"a": 1}))
        assert out == {"ok": True}

    def test_retries_on_server_error_then_succeeds(self):
        _, Resp, _ = self._patch_httpx([])
        responses = [Resp(500, None, "boom"), Resp(200, {"ok": 1})]
        patcher, _, _ = self._patch_httpx(responses)
        client = IOIntelligenceAsyncHTTPClient(
            "k", "https://x", max_retries=2, retry_delay=0
        )
        with patcher:
            out = asyncio.run(client.apost_with_retry({"a": 1}))
        assert out == {"ok": 1}

    def test_auth_error_not_retried(self):
        from langchain_iointelligence.exceptions import \
            IOIntelligenceAuthenticationError

        _, Resp, _ = self._patch_httpx([])
        responses = [Resp(401, None, "nope")]
        patcher, _, _ = self._patch_httpx(responses)
        client = IOIntelligenceAsyncHTTPClient(
            "k", "https://x", max_retries=3, retry_delay=0
        )
        with patcher:
            try:
                asyncio.run(client.apost_with_retry({"a": 1}))
                assert False, "expected auth error"
            except IOIntelligenceAuthenticationError:
                pass

    def test_client_reuse_within_same_loop(self):
        """Two calls in the same event loop must reuse a single AsyncClient."""
        _, Resp, _ = self._patch_httpx([])
        responses = [Resp(200, {"ok": 1}), Resp(200, {"ok": 2})]
        patcher, _, instances = self._patch_httpx(responses)

        client = IOIntelligenceAsyncHTTPClient("k", "https://x", max_retries=0)

        async def _two_calls():
            r1 = await client.apost_with_retry({"a": 1})
            r2 = await client.apost_with_retry({"a": 2})
            return r1, r2

        with patcher:
            r1, r2 = asyncio.run(_two_calls())

        assert r1 == {"ok": 1}
        assert r2 == {"ok": 2}
        # Only one AsyncClient instance should have been created.
        assert len(instances) == 1

    def test_aclose_sets_client_to_none(self):
        """After aclose(), _client is None; next call creates a fresh client."""
        _, Resp, _ = self._patch_httpx([])
        responses = [Resp(200, {"first": True}), Resp(200, {"second": True})]
        patcher, _, instances = self._patch_httpx(responses)

        client = IOIntelligenceAsyncHTTPClient("k", "https://x", max_retries=0)

        async def _run():
            # First call – creates client #1.
            await client.apost_with_retry({"a": 1})
            assert client._client is not None
            # Close it.
            await client.aclose()
            assert client._client is None
            # Second call – must create client #2.
            result = await client.apost_with_retry({"a": 2})
            return result

        with patcher:
            result = asyncio.run(_run())

        assert result == {"second": True}
        # Two separate AsyncClient instances must have been created.
        assert len(instances) == 2

    def test_new_client_created_across_loops(self):
        """Each asyncio.run() call gets a fresh AsyncClient (different loop)."""
        _, Resp, _ = self._patch_httpx([])
        responses = [Resp(200, {"loop": 1}), Resp(200, {"loop": 2})]
        patcher, _, instances = self._patch_httpx(responses)

        client = IOIntelligenceAsyncHTTPClient("k", "https://x", max_retries=0)

        with patcher:
            r1 = asyncio.run(client.apost_with_retry({"a": 1}))
            r2 = asyncio.run(client.apost_with_retry({"a": 2}))

        assert r1 == {"loop": 1}
        assert r2 == {"loop": 2}
        # A new client must have been created for each distinct event loop.
        assert len(instances) == 2


class TestChatModelClose:
    def test_close_calls_http_client_close_and_nones_it(self):
        """close() calls the sync client's close() and sets _http_client to None."""
        chat = _model()
        mock_sync = MagicMock()
        chat._http_client = mock_sync

        chat.close()

        mock_sync.close.assert_called_once()
        assert chat._http_client is None

    def test_close_is_noop_when_no_client(self):
        """close() is safe when _http_client is already None."""
        chat = _model()
        assert chat._http_client is None
        chat.close()  # must not raise
        assert chat._http_client is None

    def test_aclose_calls_async_http_client_aclose_and_nones_it(self):
        """aclose() awaits the async client's aclose() and sets _async_http_client to None."""
        chat = _model()
        mock_async = AsyncMock()
        chat._async_http_client = mock_async

        asyncio.run(chat.aclose())

        mock_async.aclose.assert_awaited_once()
        assert chat._async_http_client is None

    def test_aclose_is_noop_when_no_async_client(self):
        """aclose() is safe when _async_http_client is already None."""
        chat = _model()
        assert chat._async_http_client is None
        asyncio.run(chat.aclose())  # must not raise
        assert chat._async_http_client is None
