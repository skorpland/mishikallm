# What is this?
## Helper utilities
from typing import TYPE_CHECKING, Any, List, Optional, Union

import httpx

from mishikallm._logging import verbose_logger
from mishikallm.types.llms.openai import AllMessageValues

if TYPE_CHECKING:
    from opentelemetry.trace import Span as _Span

    Span = Union[_Span, Any]
else:
    Span = Any


def map_finish_reason(
    finish_reason: str,
):  # openai supports 5 stop sequences - 'stop', 'length', 'function_call', 'content_filter', 'null'
    # anthropic mapping
    if finish_reason == "stop_sequence":
        return "stop"
    # cohere mapping - https://docs.cohere.com/reference/generate
    elif finish_reason == "COMPLETE":
        return "stop"
    elif finish_reason == "MAX_TOKENS":  # cohere + vertex ai
        return "length"
    elif finish_reason == "ERROR_TOXIC":
        return "content_filter"
    elif (
        finish_reason == "ERROR"
    ):  # openai currently doesn't support an 'error' finish reason
        return "stop"
    # huggingface mapping https://huggingface.github.io/text-generation-inference/#/Text%20Generation%20Inference/generate_stream
    elif finish_reason == "eos_token" or finish_reason == "stop_sequence":
        return "stop"
    elif (
        finish_reason == "FINISH_REASON_UNSPECIFIED" or finish_reason == "STOP"
    ):  # vertex ai - got from running `print(dir(response_obj.candidates[0].finish_reason))`: ['FINISH_REASON_UNSPECIFIED', 'MAX_TOKENS', 'OTHER', 'RECITATION', 'SAFETY', 'STOP',]
        return "stop"
    elif finish_reason == "SAFETY" or finish_reason == "RECITATION":  # vertex ai
        return "content_filter"
    elif finish_reason == "STOP":  # vertex ai
        return "stop"
    elif finish_reason == "end_turn" or finish_reason == "stop_sequence":  # anthropic
        return "stop"
    elif finish_reason == "max_tokens":  # anthropic
        return "length"
    elif finish_reason == "tool_use":  # anthropic
        return "tool_calls"
    elif finish_reason == "content_filtered":
        return "content_filter"
    return finish_reason


def remove_index_from_tool_calls(
    messages: Optional[List[AllMessageValues]],
):
    if messages is not None:
        for message in messages:
            _tool_calls = message.get("tool_calls")
            if _tool_calls is not None and isinstance(_tool_calls, list):
                for tool_call in _tool_calls:
                    if (
                        isinstance(tool_call, dict) and "index" in tool_call
                    ):  # Type guard to ensure it's a dict
                        tool_call.pop("index", None)

    return


def get_mishikallm_metadata_from_kwargs(kwargs: dict):
    """
    Helper to get mishikallm metadata from all mishikallm request kwargs

    Return `mishikallm_metadata` if it exists, otherwise return `metadata`
    """
    mishikallm_params = kwargs.get("mishikallm_params", {})
    if mishikallm_params:
        metadata = mishikallm_params.get("metadata", {})
        mishikallm_metadata = mishikallm_params.get("mishikallm_metadata", {})
        if mishikallm_metadata:
            return mishikallm_metadata
        elif metadata:
            return metadata

    return {}


# Helper functions used for OTEL logging
def _get_parent_otel_span_from_kwargs(
    kwargs: Optional[dict] = None,
) -> Union[Span, None]:
    try:
        if kwargs is None:
            return None
        mishikallm_params = kwargs.get("mishikallm_params")
        _metadata = kwargs.get("metadata") or {}
        if "mishikallm_parent_otel_span" in _metadata:
            return _metadata["mishikallm_parent_otel_span"]
        elif (
            mishikallm_params is not None
            and mishikallm_params.get("metadata") is not None
            and "mishikallm_parent_otel_span" in mishikallm_params.get("metadata", {})
        ):
            return mishikallm_params["metadata"]["mishikallm_parent_otel_span"]
        elif "mishikallm_parent_otel_span" in kwargs:
            return kwargs["mishikallm_parent_otel_span"]
        return None
    except Exception as e:
        verbose_logger.exception(
            "Error in _get_parent_otel_span_from_kwargs: " + str(e)
        )
        return None


def process_response_headers(response_headers: Union[httpx.Headers, dict]) -> dict:
    from mishikallm.types.utils import OPENAI_RESPONSE_HEADERS

    openai_headers = {}
    processed_headers = {}
    additional_headers = {}

    for k, v in response_headers.items():
        if k in OPENAI_RESPONSE_HEADERS:  # return openai-compatible headers
            openai_headers[k] = v
        if k.startswith(
            "llm_provider-"
        ):  # return raw provider headers (incl. openai-compatible ones)
            processed_headers[k] = v
        else:
            additional_headers["{}-{}".format("llm_provider", k)] = v

    additional_headers = {
        **openai_headers,
        **processed_headers,
        **additional_headers,
    }
    return additional_headers
