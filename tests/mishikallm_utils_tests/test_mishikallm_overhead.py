import json
import os
import sys
import time
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock
import pytest

sys.path.insert(
    0, os.path.abspath("../..")
)  # Adds the parent directory to the system path
import mishikallm


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "model",
    [
        "bedrock/mistral.mistral-7b-instruct-v0:2",
        "openai/gpt-4o",
        "openai/self_hosted",
        "bedrock/anthropic.claude-3-5-haiku-20241022-v1:0",
    ],
)
async def test_mishikallm_overhead(model):

    mishikallm._turn_on_debug()
    start_time = datetime.now()
    if model == "openai/self_hosted":
        response = await mishikallm.acompletion(
            model=model,
            messages=[{"role": "user", "content": "Hello, world!"}],
            api_base="https://exampleopenaiendpoint-production.up.railway.app/",
        )
    else:
        response = await mishikallm.acompletion(
            model=model,
            messages=[{"role": "user", "content": "Hello, world!"}],
        )
    end_time = datetime.now()
    total_time_ms = (end_time - start_time).total_seconds() * 1000
    print(response)
    print(response._hidden_params)
    mishikallm_overhead_ms = response._hidden_params["mishikallm_overhead_time_ms"]
    # calculate percent of overhead caused by mishikallm
    overhead_percent = mishikallm_overhead_ms * 100 / total_time_ms
    print("##########################\n")
    print("total_time_ms", total_time_ms)
    print("response mishikallm_overhead_ms", mishikallm_overhead_ms)
    print("mishikallm overhead_percent {}%".format(overhead_percent))
    print("##########################\n")
    assert mishikallm_overhead_ms > 0
    assert mishikallm_overhead_ms < 1000

    # latency overhead should be less than total request time
    assert mishikallm_overhead_ms < (end_time - start_time).total_seconds() * 1000

    # latency overhead should be under 40% of total request time
    assert overhead_percent < 40

    pass


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "model",
    [
        "bedrock/mistral.mistral-7b-instruct-v0:2",
        "openai/gpt-4o",
        "bedrock/anthropic.claude-3-5-haiku-20241022-v1:0",
        "openai/self_hosted",
    ],
)
async def test_mishikallm_overhead_stream(model):

    mishikallm._turn_on_debug()
    start_time = datetime.now()
    if model == "openai/self_hosted":
        response = await mishikallm.acompletion(
            model=model,
            messages=[{"role": "user", "content": "Hello, world!"}],
            api_base="https://exampleopenaiendpoint-production.up.railway.app/",
            stream=True,
        )
    else:
        response = await mishikallm.acompletion(
            model=model,
            messages=[{"role": "user", "content": "Hello, world!"}],
            stream=True,
        )

    async for chunk in response:
        print()

    end_time = datetime.now()
    total_time_ms = (end_time - start_time).total_seconds() * 1000
    print(response)
    print(response._hidden_params)
    mishikallm_overhead_ms = response._hidden_params["mishikallm_overhead_time_ms"]
    # calculate percent of overhead caused by mishikallm
    overhead_percent = mishikallm_overhead_ms * 100 / total_time_ms
    print("##########################\n")
    print("total_time_ms", total_time_ms)
    print("response mishikallm_overhead_ms", mishikallm_overhead_ms)
    print("mishikallm overhead_percent {}%".format(overhead_percent))
    print("##########################\n")
    assert mishikallm_overhead_ms > 0
    assert mishikallm_overhead_ms < 1000

    # latency overhead should be less than total request time
    assert mishikallm_overhead_ms < (end_time - start_time).total_seconds() * 1000

    # latency overhead should be under 40% of total request time
    assert overhead_percent < 40

    pass
