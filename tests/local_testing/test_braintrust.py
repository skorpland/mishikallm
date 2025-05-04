# What is this?
## This tests the braintrust integration

import asyncio
import os
import random
import sys
import time
import traceback
from datetime import datetime

from dotenv import load_dotenv
from fastapi import Request

load_dotenv()
import os

sys.path.insert(
    0, os.path.abspath("../..")
)  # Adds the parent directory to the system path
import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import mishikallm
from mishikallm.llms.custom_httpx.http_handler import HTTPHandler


def test_braintrust_logging():
    import mishikallm

    mishikallm.set_verbose = True

    http_client = HTTPHandler()

    with patch.object(
        mishikallm.integrations.braintrust_logging.global_braintrust_sync_http_handler,
        "post",
        new=MagicMock(),
    ) as mock_client:
        # set braintrust as a callback, mishikallm will send the data to braintrust
        mishikallm.callbacks = ["braintrust"]

        # openai call
        response = mishikallm.completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hi 👋 - i'm openai"}],
        )

        time.sleep(2)
        mock_client.assert_called()

def test_braintrust_logging_specific_project_id():
    import mishikallm

    mishikallm.set_verbose = True

    with patch.object(
        mishikallm.integrations.braintrust_logging.global_braintrust_sync_http_handler,
        "post",
        new=MagicMock(),
    ) as mock_client:
        # set braintrust as a callback, mishikallm will send the data to braintrust
        mishikallm.callbacks = ["braintrust"]

        response = mishikallm.completion(model="openai/gpt-4o", messages=[{ "content": "Hello, how are you?","role": "user"}], metadata={"project_id": "123"})

        time.sleep(2)
        
        # Check that the log was inserted into the correct project
        mock_client.assert_called()
        _, kwargs = mock_client.call_args
        assert 'url' in kwargs
        assert kwargs['url'] == "https://api.braintrustdata.com/v1/project_logs/123/insert"

