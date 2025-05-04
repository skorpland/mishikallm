import copy
import json
import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(
    0, os.path.abspath("../../..")
)  # Adds the parent directory to the system path


import mishikallm


def test_update_kwargs_does_not_mutate_defaults_and_merges_metadata():
    # initialize a real Router (env‑vars can be empty)
    router = mishikallm.Router(
        model_list=[
            {
                "model_name": "gpt-3.5-turbo",
                "mishikallm_params": {
                    "model": "azure/chatgpt-v-3",
                    "api_key": os.getenv("AZURE_API_KEY"),
                    "api_version": os.getenv("AZURE_API_VERSION"),
                    "api_base": os.getenv("AZURE_API_BASE"),
                },
            }
        ],
    )

    # override to known defaults for the test
    router.default_mishikallm_params = {
        "foo": "bar",
        "metadata": {"baz": 123},
    }
    original = copy.deepcopy(router.default_mishikallm_params)
    kwargs = {}

    # invoke the helper
    router._update_kwargs_with_default_mishikallm_params(
        kwargs=kwargs,
        metadata_variable_name="mishikallm_metadata",
    )

    # 1) router.defaults must be unchanged
    assert router.default_mishikallm_params == original

    # 2) non‑metadata keys get merged
    assert kwargs["foo"] == "bar"

    # 3) metadata lands under "metadata"
    assert kwargs["mishikallm_metadata"] == {"baz": 123}


def test_router_with_model_info_and_model_group():
    """
    Test edge case where user specifies model_group in model_info
    """
    router = mishikallm.Router(
        model_list=[
            {
                "model_name": "gpt-3.5-turbo",
                "mishikallm_params": {
                    "model": "gpt-3.5-turbo",
                },
                "model_info": {
                    "tpm": 1000,
                    "rpm": 1000,
                    "model_group": "gpt-3.5-turbo",
                },
            }
        ],
    )

    router._set_model_group_info(
        model_group="gpt-3.5-turbo",
        user_facing_model_group_name="gpt-3.5-turbo",
    )


@pytest.mark.asyncio
async def test_router_with_tags_and_fallbacks():
    """
    If fallback model missing tag, raise error
    """
    from mishikallm import Router

    router = Router(
        model_list=[
            {
                "model_name": "gpt-3.5-turbo",
                "mishikallm_params": {
                    "model": "gpt-3.5-turbo",
                    "mock_response": "Hello, world!",
                    "tags": ["test"],
                },
            },
            {
                "model_name": "anthropic-claude-3-5-sonnet",
                "mishikallm_params": {
                    "model": "claude-3-5-sonnet-latest",
                    "mock_response": "Hello, world 2!",
                },
            },
        ],
        fallbacks=[
            {"gpt-3.5-turbo": ["anthropic-claude-3-5-sonnet"]},
        ],
        enable_tag_filtering=True,
    )

    with pytest.raises(Exception):
        response = await router.acompletion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, world!"}],
            mock_testing_fallbacks=True,
            metadata={"tags": ["test"]},
        )
