"""Async HTTP client (httpx) with retry logic for io Intelligence API."""

import asyncio
import json
from typing import Any, AsyncIterator, Dict, Optional

import httpx

from .exceptions import (IOIntelligenceConnectionError, IOIntelligenceError,
                         IOIntelligenceRateLimitError,
                         IOIntelligenceServerError, IOIntelligenceTimeoutError,
                         classify_api_error)


class IOIntelligenceAsyncHTTPClient:
    """Async HTTP client mirroring the sync client's retry/error behaviour."""

    def __init__(
        self,
        api_key: str,
        api_url: str,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        self.api_key = api_key
        self.api_url = api_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def apost_with_retry(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Async POST with automatic retry on rate-limit/server/network errors."""
        last_exception: Optional[IOIntelligenceError] = None

        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        self.api_url, headers=self._headers, json=data
                    )

                if response.status_code >= 400:
                    error = classify_api_error(response.status_code, response.text)
                    if isinstance(
                        error,
                        (IOIntelligenceRateLimitError, IOIntelligenceServerError),
                    ) and attempt < self.max_retries:
                        delay = self.retry_delay * (2**attempt)
                        if isinstance(error, IOIntelligenceRateLimitError):
                            delay = max(delay, 60)
                        await asyncio.sleep(delay)
                        continue
                    raise error

                result: Dict[str, Any] = response.json()
                return result

            except IOIntelligenceError:
                # Classified API errors (auth/client/non-retryable server) must
                # propagate as-is - they subclass ValueError, so they would
                # otherwise be swallowed by the JSON-decode handler below.
                raise
            except httpx.TimeoutException:
                last_exception = IOIntelligenceTimeoutError(
                    f"Request timeout after {self.timeout} seconds"
                )
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay * (2**attempt))
                    continue
            except httpx.HTTPError as exc:
                last_exception = IOIntelligenceConnectionError(
                    f"Connection error: {str(exc)}"
                )
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay * (2**attempt))
                    continue
            except ValueError as exc:  # JSON decode error - don't retry
                last_exception = IOIntelligenceError(
                    f"Invalid JSON response: {str(exc)}"
                )
                break

        raise last_exception or IOIntelligenceError("All retry attempts failed")

    async def astream(self, data: Dict[str, Any]) -> AsyncIterator[Dict[str, Any]]:
        """Async stream of parsed SSE chunk dicts from the chat endpoint."""
        headers = {**self._headers, "Accept": "text/event-stream"}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST", self.api_url, headers=headers, json=data
                ) as response:
                    if response.status_code >= 400:
                        body = await response.aread()
                        text = body.decode() if isinstance(body, bytes) else str(body)
                        raise classify_api_error(response.status_code, text)

                    async for line in response.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        payload = line[6:].strip()
                        if payload == "[DONE]":
                            break
                        try:
                            yield json.loads(payload)
                        except json.JSONDecodeError:
                            continue
        except httpx.TimeoutException:
            raise IOIntelligenceTimeoutError(
                f"Request timeout after {self.timeout} seconds"
            )
        except httpx.HTTPError as exc:
            raise IOIntelligenceConnectionError(f"Connection error: {str(exc)}")
