import sys, os
import traceback
from dotenv import load_dotenv
import asyncio, logging

load_dotenv()
import os, io

sys.path.insert(
    0, os.path.abspath("../..")
)  # Adds the parent directory to the system path
import pytest
import mishikallm
from mishikallm import (
    embedding,
    completion,
    acompletion,
    acreate,
    completion_cost,
    Timeout,
    ModelResponse,
)
from mishikallm import RateLimitError

# mishikallm.num_retries = 3
mishikallm.cache = None
mishikallm.success_callback = []
user_message = "Write a short poem about the sky"
messages = [{"content": user_message, "role": "user"}]


@pytest.fixture(autouse=True)
def reset_callbacks():
    print("\npytest fixture - resetting callbacks")
    mishikallm.success_callback = []
    mishikallm._async_success_callback = []
    mishikallm.failure_callback = []
    mishikallm.callbacks = []


@pytest.mark.skip(reason="Account rate limited.")
def test_completion_clarifai_claude_2_1():
    print("calling clarifai claude completion")
    import os

    clarifai_pat = os.environ["CLARIFAI_API_KEY"]

    try:
        response = completion(
            model="clarifai/anthropic.completion.claude-2_1",
            num_retries=3,
            messages=messages,
            max_tokens=10,
            temperature=0.1,
        )
        print(response)

    except RateLimitError:
        pass

    except Exception as e:
        pytest.fail(f"Error occured: {e}")


@pytest.mark.skip(reason="Account rate limited")
def test_completion_clarifai_mistral_large():
    try:
        mishikallm.set_verbose = True
        response: ModelResponse = completion(
            model="clarifai/mistralai.completion.mistral-small",
            messages=messages,
            num_retries=3,
            max_tokens=10,
            temperature=0.78,
        )
        # Add any assertions here to check the response
        assert len(response.choices) > 0
        assert len(response.choices[0].message.content) > 0
    except RateLimitError:
        pass
    except Exception as e:
        pytest.fail(f"Error occurred: {e}")


@pytest.mark.skip(reason="Account rate limited")
@pytest.mark.asyncio
def test_async_completion_clarifai():
    import asyncio

    mishikallm.set_verbose = True

    async def test_get_response():
        user_message = "Hello, how are you?"
        messages = [{"content": user_message, "role": "user"}]
        try:
            response = await acompletion(
                model="clarifai/openai.chat-completion.GPT-4",
                messages=messages,
                num_retries=3,
                timeout=10,
                api_key=os.getenv("CLARIFAI_API_KEY"),
            )
            print(f"response: {response}")
        except mishikallm.Timeout as e:
            pass
        except Exception as e:
            pytest.fail(f"An exception occurred: {e}")

    asyncio.run(test_get_response())
