"""Streaming support for io Intelligence API."""

import json
import logging
from typing import Any, Dict, Iterator, List, Optional

import requests
from langchain_core.messages import AIMessageChunk
from langchain_core.messages.ai import UsageMetadata
from langchain_core.messages.tool import ToolCallChunk
from langchain_core.outputs import ChatGenerationChunk

from .exceptions import IOIntelligenceError, classify_api_error

logger = logging.getLogger(__name__)


def build_generation_chunk(
    chunk_data: Dict[str, Any]
) -> Optional[ChatGenerationChunk]:
    """Build a ChatGenerationChunk from a raw SSE chunk dict.

    Shared by the sync streamer and the async stream so both paths produce
    identical chunks (content deltas, tool-call deltas, and the final
    usage-only chunk emitted when ``stream_options.include_usage`` is set).
    """
    try:
        choices = chunk_data.get("choices") or []
        usage = chunk_data.get("usage")

        # Final usage-only chunk (no choices) - surface token usage.
        if not choices:
            if usage:
                usage_metadata = UsageMetadata(
                    input_tokens=usage.get("prompt_tokens", 0),
                    output_tokens=usage.get("completion_tokens", 0),
                    total_tokens=usage.get("total_tokens", 0),
                )
                return ChatGenerationChunk(
                    message=AIMessageChunk(content="", usage_metadata=usage_metadata),
                    generation_info={
                        "model": chunk_data.get("model"),
                        "chunk_id": chunk_data.get("id"),
                    },
                )
            return None

        choice = choices[0]
        delta = choice.get("delta", {})

        content = delta.get("content") or ""
        finish_reason = choice.get("finish_reason")

        # Incremental tool-call deltas, if any.
        tool_call_chunks: List[ToolCallChunk] = []
        for raw_tool_call in delta.get("tool_calls") or []:
            function = raw_tool_call.get("function", {})
            tool_call_chunks.append(
                ToolCallChunk(
                    name=function.get("name"),
                    args=function.get("arguments"),
                    id=raw_tool_call.get("id"),
                    index=raw_tool_call.get("index"),
                    type="tool_call_chunk",
                )
            )

        if tool_call_chunks:
            message_chunk = AIMessageChunk(
                content=content, tool_call_chunks=tool_call_chunks
            )
        else:
            message_chunk = AIMessageChunk(content=content)

        return ChatGenerationChunk(
            message=message_chunk,
            generation_info={
                "finish_reason": finish_reason,
                "model": chunk_data.get("model"),
                "chunk_id": chunk_data.get("id"),
            },
        )

    except (KeyError, TypeError):
        return None


class IOIntelligenceStreamer:
    """Handles streaming responses from io Intelligence API."""

    def __init__(self, api_key: str, api_url: str, timeout: int = 30):
        self.api_key = api_key
        self.api_url = api_url
        self.timeout = timeout

    def stream_chat_completion(self, data: Dict[str, Any]) -> Iterator[ChatGenerationChunk]:
        """Stream chat completion responses.

        Args:
            data: Request data dictionary

        Yields:
            ChatGenerationChunk objects for each token/chunk
        """
        # Enable streaming in request
        stream_data = data.copy()
        stream_data["stream"] = True

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }

        try:
            with requests.post(
                self.api_url, headers=headers, json=stream_data, stream=True, timeout=self.timeout
            ) as response:
                if not response.ok:
                    error = classify_api_error(response.status_code, response.text)
                    raise error

                # Process Server-Sent Events
                for chunk in self._parse_sse_stream(response):
                    if chunk:
                        yield chunk

        except requests.exceptions.RequestException as e:
            raise IOIntelligenceError(f"Streaming request failed: {str(e)}")

    def _parse_sse_stream(self, response) -> Iterator[ChatGenerationChunk]:
        """Parse Server-Sent Events stream.

        Args:
            response: Streaming HTTP response

        Yields:
            ChatGenerationChunk objects
        """
        for line in response.iter_lines(decode_unicode=True):
            if line is None:
                continue

            # SSE format: "data: {json}" or "data: [DONE]"
            if line.startswith("data: "):
                data_part = line[6:]  # Remove "data: " prefix

                # End of stream marker
                if data_part.strip() == "[DONE]":
                    break

                try:
                    chunk_data = json.loads(data_part)
                    chunk = self._create_chat_chunk(chunk_data)
                    if chunk:
                        yield chunk

                except json.JSONDecodeError:
                    # Skip malformed JSON
                    continue
                except Exception as e:
                    # Log error but continue streaming
                    logger.warning("Error processing chunk: %s", e)
                    continue

    def _create_chat_chunk(self, chunk_data: Dict[str, Any]) -> Optional[ChatGenerationChunk]:
        """Create ChatGenerationChunk from API chunk data.

        Thin wrapper around :func:`build_generation_chunk` (kept for backward
        compatibility / instance-level access).
        """
        return build_generation_chunk(chunk_data)
