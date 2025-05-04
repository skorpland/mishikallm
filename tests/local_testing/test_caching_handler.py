import os
import sys
import time
import traceback
import uuid

from dotenv import load_dotenv

load_dotenv()
sys.path.insert(
    0, os.path.abspath("../..")
)  # Adds the parent directory to the system path
import asyncio
import hashlib
import random

import pytest

import mishikallm
from mishikallm import aembedding, completion, embedding
from mishikallm.caching.caching import Cache

from unittest.mock import AsyncMock, patch, MagicMock
from mishikallm.caching.caching_handler import LLMCachingHandler, CachingHandlerResponse
from mishikallm.caching.caching import MishikaLLMCacheType
from mishikallm.types.utils import CallTypes
from mishikallm.types.rerank import RerankResponse
from mishikallm.types.utils import (
    ModelResponse,
    EmbeddingResponse,
    TextCompletionResponse,
    TranscriptionResponse,
    Embedding,
)
from datetime import timedelta, datetime
from mishikallm.mishikallm_core_utils.mishikallm_logging import Logging as MishikaLLMLogging
from mishikallm._logging import verbose_logger
import logging


def setup_cache():
    # Set up the cache
    cache = Cache(type=MishikaLLMCacheType.LOCAL)
    mishikallm.cache = cache
    return cache


chat_completion_response = mishikallm.ModelResponse(
    id=str(uuid.uuid4()),
    choices=[
        mishikallm.Choices(
            message=mishikallm.Message(
                role="assistant", content="Hello, how can I help you today?"
            )
        )
    ],
)

text_completion_response = mishikallm.TextCompletionResponse(
    id=str(uuid.uuid4()),
    choices=[mishikallm.utils.TextChoices(text="Hello, how can I help you today?")],
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "response", [chat_completion_response, text_completion_response]
)
async def test_async_set_get_cache(response):
    mishikallm.set_verbose = True
    setup_cache()
    verbose_logger.setLevel(logging.DEBUG)
    caching_handler = LLMCachingHandler(
        original_function=completion, request_kwargs={}, start_time=datetime.now()
    )

    messages = [{"role": "user", "content": f"Unique message {datetime.now()}"}]

    logging_obj = MishikaLLMLogging(
        mishikallm_call_id=str(datetime.now()),
        call_type=CallTypes.completion.value,
        model="gpt-3.5-turbo",
        messages=messages,
        function_id=str(uuid.uuid4()),
        stream=False,
        start_time=datetime.now(),
    )

    result = response
    print("result", result)

    original_function = (
        mishikallm.acompletion
        if isinstance(response, mishikallm.ModelResponse)
        else mishikallm.atext_completion
    )
    if isinstance(response, mishikallm.ModelResponse):
        kwargs = {"messages": messages}
        call_type = CallTypes.acompletion.value
    else:
        kwargs = {"prompt": f"Hello, how can I help you today? {datetime.now()}"}
        call_type = CallTypes.atext_completion.value

    await caching_handler.async_set_cache(
        result=result, original_function=original_function, kwargs=kwargs
    )

    await asyncio.sleep(2)

    # Verify the result was cached
    cached_response = await caching_handler._async_get_cache(
        model="gpt-3.5-turbo",
        original_function=original_function,
        logging_obj=logging_obj,
        start_time=datetime.now(),
        call_type=call_type,
        kwargs=kwargs,
    )

    assert cached_response.cached_result is not None
    assert cached_response.cached_result.id == result.id


@pytest.mark.asyncio
async def test_async_log_cache_hit_on_callbacks():
    """
    Assert logging callbacks are called after a cache hit
    """
    # Setup
    caching_handler = LLMCachingHandler(
        original_function=completion, request_kwargs={}, start_time=datetime.now()
    )

    mock_logging_obj = MagicMock()
    mock_logging_obj.async_success_handler = AsyncMock()
    mock_logging_obj.success_handler = MagicMock()

    cached_result = "Mocked cached result"
    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=1)
    cache_hit = True

    # Call the method
    caching_handler._async_log_cache_hit_on_callbacks(
        logging_obj=mock_logging_obj,
        cached_result=cached_result,
        start_time=start_time,
        end_time=end_time,
        cache_hit=cache_hit,
    )

    # Wait for the async task to complete
    await asyncio.sleep(0.5)

    print("mock logging obj methods called", mock_logging_obj.mock_calls)

    # Assertions
    mock_logging_obj.async_success_handler.assert_called_once_with(
        cached_result, start_time, end_time, cache_hit
    )

    # Wait for the thread to complete
    await asyncio.sleep(0.5)

    mock_logging_obj.success_handler.assert_called_once_with(
        cached_result, start_time, end_time, cache_hit
    )


@pytest.mark.parametrize(
    "call_type, cached_result, expected_type",
    [
        (
            CallTypes.completion.value,
            {
                "id": "test",
                "choices": [{"message": {"role": "assistant", "content": "Hello"}}],
            },
            ModelResponse,
        ),
        (
            CallTypes.text_completion.value,
            {"id": "test", "choices": [{"text": "Hello"}]},
            TextCompletionResponse,
        ),
        (
            CallTypes.embedding.value,
            {"data": [{"embedding": [0.1, 0.2, 0.3]}]},
            EmbeddingResponse,
        ),
        (
            CallTypes.rerank.value,
            {"id": "test", "results": [{"index": 0, "relevance_score": 0.9}]},
            RerankResponse,
        ),
        (
            CallTypes.transcription.value,
            {"text": "Hello, world!"},
            TranscriptionResponse,
        ),
    ],
)
def test_convert_cached_result_to_model_response(
    call_type, cached_result, expected_type
):
    """
    Assert that the cached result is converted to the correct type
    """
    caching_handler = LLMCachingHandler(
        original_function=lambda: None, request_kwargs={}, start_time=datetime.now()
    )
    logging_obj = MishikaLLMLogging(
        mishikallm_call_id=str(datetime.now()),
        call_type=call_type,
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello, how can I help you today?"}],
        function_id=str(uuid.uuid4()),
        stream=False,
        start_time=datetime.now(),
    )

    result = caching_handler._convert_cached_result_to_model_response(
        cached_result=cached_result,
        call_type=call_type,
        kwargs={},
        logging_obj=logging_obj,
        model="test-model",
        args=(),
    )

    assert isinstance(result, expected_type)
    assert result is not None


def test_combine_cached_embedding_response_with_api_result():
    """
    If the cached response has [cache_hit, None, cache_hit]
    result should be [cache_hit, api_result, cache_hit]
    """
    # Setup
    caching_handler = LLMCachingHandler(
        original_function=lambda: None, request_kwargs={}, start_time=datetime.now()
    )

    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=1)

    # Create a CachingHandlerResponse with some cached and some None values
    cached_response = EmbeddingResponse(
        data=[
            Embedding(embedding=[0.1, 0.2, 0.3], index=0, object="embedding"),
            None,
            Embedding(embedding=[0.7, 0.8, 0.9], index=2, object="embedding"),
        ]
    )
    caching_handler_response = CachingHandlerResponse(
        final_embedding_cached_response=cached_response
    )

    # Create an API EmbeddingResponse for the missing value
    api_response = EmbeddingResponse(
        data=[Embedding(embedding=[0.4, 0.5, 0.6], index=1, object="embedding")]
    )

    # Call the method
    result = caching_handler._combine_cached_embedding_response_with_api_result(
        _caching_handler_response=caching_handler_response,
        embedding_response=api_response,
        start_time=start_time,
        end_time=end_time,
    )

    # Assertions
    assert isinstance(result, EmbeddingResponse)
    assert len(result.data) == 3
    assert result.data[0].embedding == [0.1, 0.2, 0.3]
    assert result.data[1].embedding == [0.4, 0.5, 0.6]
    assert result.data[2].embedding == [0.7, 0.8, 0.9]
    assert result._hidden_params["cache_hit"] == True
    assert isinstance(result._response_ms, float)
    assert result._response_ms > 0


def test_combine_cached_embedding_response_multiple_missing_values():
    """
    If the cached response has [cache_hit, None, None, cache_hit, None]
    result should be            [cache_hit, api_result, api_result, cache_hit, api_result]
    """

    # Setup
    caching_handler = LLMCachingHandler(
        original_function=lambda: None, request_kwargs={}, start_time=datetime.now()
    )

    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=1)

    # Create a CachingHandlerResponse with some cached and some None values
    cached_response = EmbeddingResponse(
        data=[
            Embedding(embedding=[0.1, 0.2, 0.3], index=0, object="embedding"),
            None,
            None,
            Embedding(embedding=[0.7, 0.8, 0.9], index=3, object="embedding"),
            None,
        ]
    )

    caching_handler_response = CachingHandlerResponse(
        final_embedding_cached_response=cached_response
    )

    # Create an API EmbeddingResponse for the missing values
    api_response = EmbeddingResponse(
        data=[
            Embedding(embedding=[0.4, 0.5, 0.6], index=1, object="embedding"),
            Embedding(embedding=[0.4, 0.5, 0.6], index=2, object="embedding"),
            Embedding(embedding=[0.4, 0.5, 0.6], index=4, object="embedding"),
        ]
    )

    # Call the method
    result = caching_handler._combine_cached_embedding_response_with_api_result(
        _caching_handler_response=caching_handler_response,
        embedding_response=api_response,
        start_time=start_time,
        end_time=end_time,
    )

    # Assertions
    assert isinstance(result, EmbeddingResponse)
    assert len(result.data) == 5
    assert result.data[0].embedding == [0.1, 0.2, 0.3]
    assert result.data[1].embedding == [0.4, 0.5, 0.6]
    assert result.data[2].embedding == [0.4, 0.5, 0.6]
    assert result.data[3].embedding == [0.7, 0.8, 0.9]
