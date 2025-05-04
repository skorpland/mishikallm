"""
*New config* for using aiohttp to make the request to the custom OpenAI-like provider

This leads to 10x higher RPS than httpx
https://github.com/BerriAI/mishikallm/issues/6592

New config to ensure we introduce this without causing breaking changes for users
"""

from typing import TYPE_CHECKING, Any, List, Optional

from aiohttp import ClientResponse

from mishikallm.llms.openai_like.chat.transformation import OpenAILikeChatConfig
from mishikallm.types.llms.openai import AllMessageValues
from mishikallm.types.utils import Choices, ModelResponse

if TYPE_CHECKING:
    from mishikallm.mishikallm_core_utils.mishikallm_logging import Logging as _MishikaLLMLoggingObj

    MishikaLLMLoggingObj = _MishikaLLMLoggingObj
else:
    MishikaLLMLoggingObj = Any


class AiohttpOpenAIChatConfig(OpenAILikeChatConfig):
    def get_complete_url(
        self,
        api_base: Optional[str],
        api_key: Optional[str],
        model: str,
        optional_params: dict,
        mishikallm_params: dict,
        stream: Optional[bool] = None,
    ) -> str:
        """
        Ensure - /v1/chat/completions is at the end of the url

        """
        if api_base is None:
            api_base = "https://api.openai.com"

        if not api_base.endswith("/chat/completions"):
            api_base += "/chat/completions"
        return api_base

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
        return {"Authorization": f"Bearer {api_key}"}

    async def transform_response(  # type: ignore
        self,
        model: str,
        raw_response: ClientResponse,
        model_response: ModelResponse,
        logging_obj: MishikaLLMLoggingObj,
        request_data: dict,
        messages: List[AllMessageValues],
        optional_params: dict,
        mishikallm_params: dict,
        encoding: Any,
        api_key: Optional[str] = None,
        json_mode: Optional[bool] = None,
    ) -> ModelResponse:
        _json_response = await raw_response.json()
        model_response.id = _json_response.get("id")
        model_response.choices = [
            Choices(**choice) for choice in _json_response.get("choices")
        ]
        model_response.created = _json_response.get("created")
        model_response.model = _json_response.get("model")
        model_response.object = _json_response.get("object")
        model_response.system_fingerprint = _json_response.get("system_fingerprint")
        return model_response
