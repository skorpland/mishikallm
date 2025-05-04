from typing import List, Optional, Union

import httpx

import mishikallm
from mishikallm.llms.base_llm.base_utils import BaseLLMModelInfo
from mishikallm.llms.base_llm.chat.transformation import BaseLLMException
from mishikallm.secret_managers.main import get_secret_str
from mishikallm.types.llms.openai import AllMessageValues
from mishikallm.utils import _add_path_to_api_base


class VLLMError(BaseLLMException):
    pass


class VLLMModelInfo(BaseLLMModelInfo):
    def validate_environment(
        self,
        headers: dict,
        model: str,
        messages: List[AllMessageValues],
        optional_params: dict,
        mishikallm_params: dict,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
    ) -> dict:
        """Google AI Studio sends api key in query params"""
        return headers

    @staticmethod
    def get_api_base(api_base: Optional[str] = None) -> Optional[str]:
        api_base = api_base or get_secret_str("VLLM_API_BASE")
        if api_base is None:
            raise ValueError(
                "VLLM_API_BASE is not set. Please set the environment variable, to use VLLM's pass-through - `{MISHIKALLM_API_BASE}/vllm/{endpoint}`."
            )
        return api_base

    @staticmethod
    def get_api_key(api_key: Optional[str] = None) -> Optional[str]:
        return None

    @staticmethod
    def get_base_model(model: str) -> Optional[str]:
        return model

    def get_models(
        self, api_key: Optional[str] = None, api_base: Optional[str] = None
    ) -> List[str]:
        api_base = VLLMModelInfo.get_api_base(api_base)
        api_key = VLLMModelInfo.get_api_key(api_key)
        endpoint = "/v1/models"
        if api_base is None or api_key is None:
            raise ValueError(
                "GEMINI_API_BASE or GEMINI_API_KEY is not set. Please set the environment variable, to query Gemini's `/models` endpoint."
            )

        url = _add_path_to_api_base(api_base, endpoint)
        response = mishikallm.module_level_client.get(
            url=url,
        )

        response.raise_for_status()

        models = response.json()["data"]

        return [model["id"] for model in models]

    def get_error_class(
        self, error_message: str, status_code: int, headers: Union[dict, httpx.Headers]
    ) -> BaseLLMException:
        return VLLMError(
            status_code=status_code, message=error_message, headers=headers
        )
