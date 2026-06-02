"""Enhanced IOIntelligenceChatModel implementation for LangChain."""

import json
import os
from operator import itemgetter
from typing import (Any, AsyncIterator, Callable, Dict, Iterator, List,
                    Literal, Optional, Sequence, Type, Union)

from dotenv import load_dotenv
from langchain_core.callbacks.manager import (AsyncCallbackManagerForLLMRun,
                                              CallbackManagerForLLMRun)
from langchain_core.language_models import LanguageModelInput
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (AIMessage, BaseMessage, HumanMessage,
                                     SystemMessage, ToolMessage)
from langchain_core.messages.ai import UsageMetadata
from langchain_core.output_parsers import (JsonOutputParser,
                                           PydanticOutputParser)
from langchain_core.output_parsers.openai_tools import (
    JsonOutputKeyToolsParser, PydanticToolsParser, make_invalid_tool_call,
    parse_tool_call)
from langchain_core.outputs import (ChatGeneration, ChatGenerationChunk,
                                    ChatResult)
from langchain_core.runnables import Runnable, RunnableMap, RunnablePassthrough
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_tool
from langchain_core.utils.pydantic import is_basemodel_subclass
from pydantic import BaseModel

try:
    from .async_http_client import IOIntelligenceAsyncHTTPClient
    from .exceptions import (IOIntelligenceError,
                             IOIntelligenceInvalidResponseError)
    from .http_client import IOIntelligenceHTTPClient
    from .streaming import IOIntelligenceStreamer, build_generation_chunk
    from .utils import IOIntelligenceUtils
except ImportError:
    # Fallback for basic functionality if enhanced modules aren't available
    IOIntelligenceHTTPClient = None
    IOIntelligenceAsyncHTTPClient = None
    IOIntelligenceStreamer = None
    build_generation_chunk = None
    IOIntelligenceError = Exception
    IOIntelligenceInvalidResponseError = Exception
    IOIntelligenceUtils = None

    import requests
    from langchain_core.exceptions import \
        OutputParserException as GenerationError

# Load environment variables from .env file
load_dotenv()


def _lc_tool_call_to_openai(tool_call: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a LangChain ToolCall dict to the OpenAI tool_call wire format."""
    return {
        "id": tool_call.get("id"),
        "type": "function",
        "function": {
            "name": tool_call["name"],
            "arguments": json.dumps(tool_call.get("args", {})),
        },
    }


def _convert_message_to_dict(message: BaseMessage) -> Dict[str, Any]:
    """Convert a single LangChain message to the OpenAI chat message format."""
    if isinstance(message, HumanMessage):
        return {"role": "user", "content": message.content}
    if isinstance(message, SystemMessage):
        return {"role": "system", "content": message.content}
    if isinstance(message, ToolMessage):
        return {
            "role": "tool",
            "content": message.content,
            "tool_call_id": message.tool_call_id,
        }
    if isinstance(message, AIMessage):
        result: Dict[str, Any] = {
            "role": "assistant",
            "content": message.content or "",
        }
        # Prefer the structured tool_calls; fall back to any raw payload.
        if message.tool_calls:
            result["tool_calls"] = [
                _lc_tool_call_to_openai(tc) for tc in message.tool_calls
            ]
            # OpenAI-compatible APIs expect content to be null when only
            # tool calls are present.
            if not message.content:
                result["content"] = None
        elif message.additional_kwargs.get("tool_calls"):
            result["tool_calls"] = message.additional_kwargs["tool_calls"]
        return result
    # Generic / unknown message types default to a user turn.
    return {"role": "user", "content": message.content}


def _parse_response_tool_calls(message: Dict[str, Any]) -> tuple:
    """Parse raw OpenAI tool_calls into LangChain (valid, invalid) lists."""
    tool_calls: List[Dict[str, Any]] = []
    invalid_tool_calls: List[Dict[str, Any]] = []
    for raw_tool_call in message.get("tool_calls") or []:
        try:
            parsed = parse_tool_call(raw_tool_call, return_id=True)
            if parsed is not None:
                tool_calls.append(parsed)
        except Exception as exc:  # noqa: BLE001 - surfaced as invalid tool call
            invalid_tool_calls.append(
                make_invalid_tool_call(raw_tool_call, str(exc))
            )
    return tool_calls, invalid_tool_calls


def _format_tool_choice(
    tool_choice: Union[str, bool, dict], tool_names: List[str]
) -> Union[str, dict]:
    """Normalise a user-supplied tool_choice into the OpenAI wire format."""
    if isinstance(tool_choice, bool):
        return "required" if tool_choice else "none"
    if isinstance(tool_choice, dict):
        return tool_choice
    if tool_choice in ("auto", "none", "required"):
        return tool_choice
    if tool_choice == "any":
        return "required"
    # Treat any other string as the name of a specific tool to force.
    if tool_choice in tool_names:
        return {"type": "function", "function": {"name": tool_choice}}
    # Unknown string - pass through and let the API validate it.
    return tool_choice


class IOIntelligenceChatModel(BaseChatModel):
    """Enhanced LangChain ChatModel wrapper for io Intelligence API."""

    # Declare all fields that will be used
    io_api_key: str = ""
    io_api_url: str = ""
    model: str = "meta-llama/Llama-3.3-70B-Instruct"
    max_tokens: int = 1000
    temperature: float = 0.7
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    streaming: bool = False

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        base_url: Optional[str] = None,  # OpenAI-compatible base_url
        model: str = "meta-llama/Llama-3.3-70B-Instruct",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        streaming: bool = False,
        **kwargs,
    ):
        """Initialize IOIntelligenceChatModel.

        Args:
            api_key: io Intelligence API key (optional, defaults to IO_API_KEY env var)
            api_url: io Intelligence API URL (optional, defaults to IO_API_URL env var)
            base_url: Base URL for OpenAI-compatible interface (auto-adds /v1/chat/completions)
            model: Model name to use (default: "meta-llama/Llama-3.3-70B-Instruct")
            max_tokens: Maximum tokens to generate (default: 1000)
            temperature: Temperature for generation (default: 0.7)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retries (default: 3)
            retry_delay: Initial retry delay in seconds (default: 1.0)
            streaming: Enable streaming responses (default: False)
        """
        # Extract and set API credentials
        api_key = api_key or os.getenv("IO_API_KEY")
        
        # Handle base_url vs api_url
        if base_url and not api_url:
            # Auto-detect and append endpoint if needed
            if base_url.endswith('/chat/completions'):
                api_url = base_url
            elif base_url.endswith('/v1'):
                api_url = f"{base_url}/chat/completions"
            else:
                api_url = f"{base_url}/v1/chat/completions"
        else:
            api_url = api_url or os.getenv("IO_API_URL")

        if not api_key:
            raise ValueError(
                "IO_API_KEY must be provided either as parameter or environment variable"
            )
        if not api_url:
            raise ValueError(
                "IO_API_URL must be provided either as parameter or environment variable"
            )

        # Set field values explicitly
        kwargs.update(
            {
                "io_api_key": api_key,
                "io_api_url": api_url,
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "timeout": timeout,
                "max_retries": max_retries,
                "retry_delay": retry_delay,
                "streaming": streaming,
            }
        )

        super().__init__(**kwargs)

        # Initialize enhanced features if available
        self._http_client: Optional[Any] = None
        self._async_http_client: Optional[Any] = None
        self._streamer: Optional[Any] = None
        self._utils: Optional[Any] = None

    @property
    def _llm_type(self) -> str:
        """Return identifier of LLM type."""
        return "io_intelligence_chat"

    @property
    def http_client(self):
        """Get or create HTTP client."""
        if IOIntelligenceHTTPClient is not None and self._http_client is None:
            self._http_client = IOIntelligenceHTTPClient(
                api_key=self.io_api_key,
                api_url=self.io_api_url,
                timeout=self.timeout,
                max_retries=self.max_retries,
                retry_delay=self.retry_delay,
            )
        return self._http_client

    @property
    def async_http_client(self):
        """Get or create the async HTTP client."""
        if (
            IOIntelligenceAsyncHTTPClient is not None
            and self._async_http_client is None
        ):
            self._async_http_client = IOIntelligenceAsyncHTTPClient(
                api_key=self.io_api_key,
                api_url=self.io_api_url,
                timeout=self.timeout,
                max_retries=self.max_retries,
                retry_delay=self.retry_delay,
            )
        return self._async_http_client

    @property
    def streamer(self):
        """Get or create streaming client."""
        if IOIntelligenceStreamer and self._streamer is None:
            self._streamer = IOIntelligenceStreamer(
                api_key=self.io_api_key, api_url=self.io_api_url, timeout=self.timeout
            )
        return self._streamer

    @property
    def utils(self):
        """Get or create utilities client."""
        if IOIntelligenceUtils and self._utils is None:
            self._utils = IOIntelligenceUtils(
                api_key=self.io_api_key, api_url=self.io_api_url, timeout=self.timeout
            )
        return self._utils

    def _convert_messages_to_api_format(
        self, messages: List[BaseMessage]
    ) -> List[Dict[str, Any]]:
        """Convert LangChain messages to API format.

        Handles human/system/AI/tool roles, including assistant tool calls and
        tool results, so multi-turn tool-calling conversations round-trip
        correctly.
        """
        return [_convert_message_to_dict(message) for message in messages]

    def _build_request_data(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]],
        *,
        stream: bool = False,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Assemble the OpenAI-compatible request payload."""
        data: Dict[str, Any] = {
            "model": self.model,
            "messages": self._convert_messages_to_api_format(messages),
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        if stop:
            data["stop"] = stop
        if stream:
            data["stream"] = True
            # Ask for token usage in the final SSE chunk (caller may override).
            data.setdefault("stream_options", {"include_usage": True})
        data.update(kwargs)
        return data

    def _invalid_response_error(self, message: str) -> Exception:
        """Build the appropriate invalid-response error instance."""
        error_class = (
            IOIntelligenceInvalidResponseError
            if IOIntelligenceInvalidResponseError != Exception
            else GenerationError
        )
        return error_class(message)

    def _wrap_error(self, error: Exception) -> Exception:
        """Normalise an arbitrary error into an IOIntelligence error."""
        if IOIntelligenceError != Exception and isinstance(error, IOIntelligenceError):
            return error
        if IOIntelligenceError != Exception:
            return IOIntelligenceError(f"API request failed: {str(error)}")
        return GenerationError(f"API request failed: {str(error)}")

    def _create_chat_result(self, response_data: Dict[str, Any]) -> ChatResult:
        """Parse an API response into a ChatResult (shared by sync and async)."""
        if "choices" not in response_data or not response_data["choices"]:
            raise self._invalid_response_error("No choices in API response")

        choice = response_data["choices"][0]
        tool_calls: List[Dict[str, Any]] = []
        invalid_tool_calls: List[Dict[str, Any]] = []

        # Chat format: choices[0].message (content and/or tool_calls)
        if "message" in choice:
            response_message = choice["message"]
            content = response_message.get("content") or ""
            tool_calls, invalid_tool_calls = _parse_response_tool_calls(
                response_message
            )
        # Completion format: choices[0].text
        elif "text" in choice:
            content = choice["text"]
        else:
            raise self._invalid_response_error(
                "Unsupported response schema - expected 'message.content' or 'text' in choices"
            )

        raw_usage = response_data.get("usage") or {}
        usage_metadata = UsageMetadata(
            input_tokens=raw_usage.get("prompt_tokens", 0),
            output_tokens=raw_usage.get("completion_tokens", 0),
            total_tokens=raw_usage.get("total_tokens", 0),
        )

        message = AIMessage(
            content=content,
            tool_calls=tool_calls,
            invalid_tool_calls=invalid_tool_calls,
            usage_metadata=usage_metadata,
            response_metadata={
                "token_usage": raw_usage,
                "model": response_data.get("model", self.model),
                "finish_reason": choice.get("finish_reason"),
                "id": response_data.get("id"),
                "created": response_data.get("created"),
            },
        )

        generation = ChatGeneration(
            message=message,
            generation_info={
                "model": self.model,
                "usage": raw_usage,  # Backward compatibility
                "finish_reason": choice.get("finish_reason"),
                "response_id": response_data.get("id"),
                "created": response_data.get("created"),
            },
        )

        return ChatResult(
            generations=[generation],
            llm_output={
                "token_usage": usage_metadata,
                "model_name": self.model,
            },
        )

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Run the LLM on the given messages."""
        data = self._build_request_data(messages, stop, **kwargs)
        try:
            if self.http_client is not None:
                response_data = self.http_client.post_with_retry(data)
            else:
                response_data = self._fallback_request(data)
            return self._create_chat_result(response_data)
        except Exception as e:
            raise self._wrap_error(e)

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Asynchronously run the LLM on the given messages (native async)."""
        if self.async_http_client is None:
            # No httpx available - fall back to the base thread-pool behaviour.
            return await super()._agenerate(
                messages, stop=stop, run_manager=run_manager, **kwargs
            )
        data = self._build_request_data(messages, stop, **kwargs)
        try:
            response_data = await self.async_http_client.apost_with_retry(data)
            return self._create_chat_result(response_data)
        except Exception as e:
            raise self._wrap_error(e)

    def _fallback_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback HTTP request without enhanced features."""
        headers = {
            "Authorization": f"Bearer {self.io_api_key}",
            "Content-Type": "application/json",
        }

        response = requests.post(self.io_api_url, headers=headers, json=data, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        """Stream the LLM on the given messages."""
        # If streaming is available, use it
        if self.streamer:
            data = self._build_request_data(messages, stop, stream=True, **kwargs)

            try:
                for chunk in self.streamer.stream_chat_completion(data):
                    if run_manager:
                        run_manager.on_llm_new_token(chunk.message.content or "")
                    yield chunk
            except Exception as e:
                error_class = (
                    IOIntelligenceError if IOIntelligenceError != Exception else GenerationError
                )
                raise error_class(f"API request failed: Streaming error - {str(e)}")
        else:
            # Fallback: use non-streaming and yield complete response
            result = self._generate(messages, stop, run_manager, **kwargs)
            chunk = ChatGenerationChunk(
                message=result.generations[0].message,
                generation_info=result.generations[0].generation_info,
            )
            yield chunk

    async def _astream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        """Asynchronously stream the LLM on the given messages (native async)."""
        if self.async_http_client is None or build_generation_chunk is None:
            # No httpx available - defer to base async-over-sync streaming.
            async for chunk in super()._astream(
                messages, stop=stop, run_manager=run_manager, **kwargs
            ):
                yield chunk
            return

        data = self._build_request_data(messages, stop, stream=True, **kwargs)
        try:
            async for raw_chunk in self.async_http_client.astream(data):
                chunk = build_generation_chunk(raw_chunk)
                if chunk is None:
                    continue
                if run_manager:
                    await run_manager.on_llm_new_token(chunk.message.content or "")
                yield chunk
        except Exception as e:
            raise self._wrap_error(e)

    def bind_tools(
        self,
        tools: Sequence[Union[Dict[str, Any], type, Callable, BaseTool]],
        *,
        tool_choice: Optional[Union[str, bool, dict]] = None,
        **kwargs: Any,
    ) -> Runnable[LanguageModelInput, BaseMessage]:
        """Bind tool-like objects to this model for tool/function calling.

        Args:
            tools: Tool definitions - any object understood by
                ``convert_to_openai_tool`` (Pydantic models, ``@tool`` functions,
                ``BaseTool`` instances, plain functions, or OpenAI tool dicts).
            tool_choice: Controls which tool is invoked. One of ``"auto"``,
                ``"none"``, ``"required"``/``"any"``/``True``, a specific tool
                name, or an explicit OpenAI ``tool_choice`` dict.

        Returns:
            A runnable that always sends the bound tools to the API.
        """
        formatted_tools = [convert_to_openai_tool(tool) for tool in tools]
        if tool_choice is not None:
            tool_names = [t["function"]["name"] for t in formatted_tools]
            kwargs["tool_choice"] = _format_tool_choice(tool_choice, tool_names)
        return super().bind(tools=formatted_tools, **kwargs)

    def with_structured_output(
        self,
        schema: Union[Dict, type],
        *,
        method: Literal[
            "function_calling", "json_schema", "json_mode"
        ] = "function_calling",
        include_raw: bool = False,
        **kwargs: Any,
    ) -> Runnable[LanguageModelInput, Union[Dict, BaseModel]]:
        """Return a runnable that produces structured output matching ``schema``.

        Args:
            schema: A Pydantic ``BaseModel`` subclass, a TypedDict, or an OpenAI
                function/JSON-schema dict describing the desired output.
            method: How to enforce structure:
                ``"function_calling"`` (default) forces a tool call;
                ``"json_schema"`` uses the API's ``response_format`` json_schema;
                ``"json_mode"`` requests a generic JSON object (the schema must
                be described in the prompt).
            include_raw: When True, return ``{"raw", "parsed", "parsing_error"}``
                instead of just the parsed value.

        Returns:
            A runnable emitting the parsed object (or the raw/parsed/error dict).
        """
        if schema is None:
            raise ValueError("schema must be provided to with_structured_output")

        is_pydantic_schema = isinstance(schema, type) and is_basemodel_subclass(
            schema
        )

        if method == "function_calling":
            tool_name = convert_to_openai_tool(schema)["function"]["name"]
            llm = self.bind_tools([schema], tool_choice=tool_name)
            if is_pydantic_schema:
                output_parser: Runnable = PydanticToolsParser(
                    tools=[schema], first_tool_only=True
                )
            else:
                output_parser = JsonOutputKeyToolsParser(
                    key_name=tool_name, first_tool_only=True
                )
        elif method == "json_schema":
            function = convert_to_openai_tool(schema)["function"]
            response_format = {
                "type": "json_schema",
                "json_schema": {
                    "name": function["name"],
                    "schema": function["parameters"],
                    "strict": True,
                },
            }
            llm = self.bind(response_format=response_format)
            output_parser = (
                PydanticOutputParser(pydantic_object=schema)
                if is_pydantic_schema
                else JsonOutputParser()
            )
        elif method == "json_mode":
            llm = self.bind(response_format={"type": "json_object"})
            output_parser = (
                PydanticOutputParser(pydantic_object=schema)
                if is_pydantic_schema
                else JsonOutputParser()
            )
        else:
            raise ValueError(
                f"Unsupported method '{method}'. Expected one of "
                "'function_calling', 'json_schema', 'json_mode'."
            )

        if include_raw:
            parser_assign = RunnablePassthrough.assign(
                parsed=itemgetter("raw") | output_parser,
                parsing_error=lambda _: None,
            )
            parser_none = RunnablePassthrough.assign(parsed=lambda _: None)
            parser_with_fallback = parser_assign.with_fallbacks(
                [parser_none], exception_key="parsing_error"
            )
            return RunnableMap(raw=llm) | parser_with_fallback
        return llm | output_parser

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return a dictionary of identifying parameters."""
        return {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "streaming": self.streaming,
        }


# Alias for backward compatibility
IOIntelligenceChat = IOIntelligenceChatModel
