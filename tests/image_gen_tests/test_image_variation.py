# What this tests?
## This tests the mishikallm support for the openai /generations endpoint

import logging
import os
import sys
import traceback


sys.path.insert(
    0, os.path.abspath("../..")
)  # Adds the parent directory to the system path

from dotenv import load_dotenv
from openai.types.image import Image
from mishikallm.caching import InMemoryCache

logging.basicConfig(level=logging.DEBUG)
load_dotenv()
import asyncio
import os
import pytest

import mishikallm
import json
import tempfile
from base_image_generation_test import BaseImageGenTest
import logging
from mishikallm._logging import verbose_logger
import requests
from io import BytesIO

verbose_logger.setLevel(logging.DEBUG)


@pytest.fixture
def image_url():
    # URL of the image
    image_url = "https://mishikallm-listing.s3.amazonaws.com/mishikallm_logo.png"

    # Fetch the image from the URL
    response = requests.get(image_url)
    print(response)
    response.raise_for_status()  # Ensure the request was successful

    # Load the image into a file-like object
    image_file = BytesIO(response.content)

    return image_file


def test_openai_image_variation_openai_sdk(image_url):
    from openai import OpenAI

    client = OpenAI()
    response = client.images.create_variation(image=image_url, n=2, size="1024x1024")
    print(response)


@pytest.mark.parametrize("sync_mode", [True, False])
@pytest.mark.asyncio
async def test_openai_image_variation_mishikallm_sdk(image_url, sync_mode):
    from mishikallm import image_variation, aimage_variation

    if sync_mode:
        image_variation(image=image_url, n=2, size="1024x1024")
    else:
        await aimage_variation(image=image_url, n=2, size="1024x1024")


def test_topaz_image_variation(image_url):
    from mishikallm import image_variation, aimage_variation
    from mishikallm.llms.custom_httpx.http_handler import HTTPHandler
    from unittest.mock import patch

    client = HTTPHandler()
    with patch.object(client, "post") as mock_post:
        try:
            image_variation(
                model="topaz/Standard V2",
                image=image_url,
                n=2,
                size="1024x1024",
                client=client,
            )
        except Exception as e:
            print(e)
        mock_post.assert_called_once()
