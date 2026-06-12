"""Tests for streaming.py: resilience and logger warning on chunk errors."""

import logging
from unittest.mock import MagicMock, patch

from langchain_core.messages import AIMessageChunk
from langchain_core.outputs import ChatGenerationChunk

from langchain_iointelligence.streaming import IOIntelligenceStreamer


def _make_fake_response(data_lines):
    """Return a mock response whose iter_lines yields the given lines."""
    mock_response = MagicMock()
    mock_response.iter_lines.return_value = iter(data_lines)
    return mock_response


class TestParseSSEStreamResilience:
    def test_stream_continues_after_chunk_error(self):
        """If _create_chat_chunk raises, subsequent chunks must still be yielded."""
        streamer = IOIntelligenceStreamer("key", "https://example.com")

        # Two valid SSE lines
        lines = [
            'data: {"choices": [{"delta": {"content": "hello"}, "finish_reason": null}]}',
            'data: {"choices": [{"delta": {"content": " world"}, "finish_reason": "stop"}]}',
        ]
        fake_response = _make_fake_response(lines)

        # Good chunk for second call
        good_chunk = ChatGenerationChunk(
            message=AIMessageChunk(content=" world"),
            generation_info={},
        )

        with patch.object(
            IOIntelligenceStreamer,
            "_create_chat_chunk",
            side_effect=[Exception("forced error"), good_chunk],
        ):
            results = list(streamer._parse_sse_stream(fake_response))

        # Only the second (good) chunk should be yielded
        assert len(results) == 1
        assert results[0] is good_chunk

    def test_warning_logged_on_chunk_error(self, caplog):
        """logger.warning must be called when _create_chat_chunk raises."""
        streamer = IOIntelligenceStreamer("key", "https://example.com")

        lines = [
            'data: {"choices": [{"delta": {"content": "hi"}, "finish_reason": null}]}',
        ]
        fake_response = _make_fake_response(lines)

        with patch.object(
            IOIntelligenceStreamer,
            "_create_chat_chunk",
            side_effect=Exception("test error"),
        ):
            with caplog.at_level(logging.WARNING, logger="langchain_iointelligence.streaming"):
                list(streamer._parse_sse_stream(fake_response))

        assert any("test error" in record.message for record in caplog.records)
        assert any(record.levelno == logging.WARNING for record in caplog.records)
