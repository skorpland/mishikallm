import time
from typing import Any, Optional

import mishikallm
from mishikallm import CustomLLM, ImageObject, ImageResponse, completion, get_llm_provider
from mishikallm.llms.custom_httpx.http_handler import AsyncHTTPHandler
from mishikallm.types.utils import ModelResponse


class MyCustomLLM(CustomLLM):
    def completion(self, *args, **kwargs) -> ModelResponse:
        return mishikallm.completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello world"}],
            mock_response="Hi!",
        )  # type: ignore

    async def acompletion(self, *args, **kwargs) -> mishikallm.ModelResponse:
        return mishikallm.completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello world"}],
            mock_response="Hi!",
        )  # type: ignore


my_custom_llm = MyCustomLLM()
