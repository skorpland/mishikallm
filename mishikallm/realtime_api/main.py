"""Abstraction function for OpenAI's realtime API"""

from typing import Any, Optional

import mishikallm
from mishikallm import get_llm_provider
from mishikallm.secret_managers.main import get_secret_str
from mishikallm.types.router import GenericMishikaLLMParams

from ..mishikallm_core_utils.get_mishikallm_params import get_mishikallm_params
from ..mishikallm_core_utils.mishikallm_logging import Logging as MishikaLLMLogging
from ..llms.azure.realtime.handler import AzureOpenAIRealtime
from ..llms.openai.realtime.handler import OpenAIRealtime
from ..utils import client as wrapper_client

azure_realtime = AzureOpenAIRealtime()
openai_realtime = OpenAIRealtime()


@wrapper_client
async def _arealtime(
    model: str,
    websocket: Any,  # fastapi websocket
    api_base: Optional[str] = None,
    api_key: Optional[str] = None,
    api_version: Optional[str] = None,
    azure_ad_token: Optional[str] = None,
    client: Optional[Any] = None,
    timeout: Optional[float] = None,
    **kwargs,
):
    """
    Private function to handle the realtime API call.

    For PROXY use only.
    """
    mishikallm_logging_obj: MishikaLLMLogging = kwargs.get("mishikallm_logging_obj")  # type: ignore
    user = kwargs.get("user", None)
    mishikallm_params = GenericMishikaLLMParams(**kwargs)

    mishikallm_params_dict = get_mishikallm_params(**kwargs)

    model, _custom_llm_provider, dynamic_api_key, dynamic_api_base = get_llm_provider(
        model=model,
        api_base=api_base,
        api_key=api_key,
    )

    mishikallm_logging_obj.update_environment_variables(
        model=model,
        user=user,
        optional_params={},
        mishikallm_params=mishikallm_params_dict,
        custom_llm_provider=_custom_llm_provider,
    )

    if _custom_llm_provider == "azure":
        api_base = (
            dynamic_api_base
            or mishikallm_params.api_base
            or mishikallm.api_base
            or get_secret_str("AZURE_API_BASE")
        )
        # set API KEY
        api_key = (
            dynamic_api_key
            or mishikallm.api_key
            or mishikallm.openai_key
            or get_secret_str("AZURE_API_KEY")
        )

        await azure_realtime.async_realtime(
            model=model,
            websocket=websocket,
            api_base=api_base,
            api_key=api_key,
            api_version="2024-10-01-preview",
            azure_ad_token=None,
            client=None,
            timeout=timeout,
            logging_obj=mishikallm_logging_obj,
        )
    elif _custom_llm_provider == "openai":
        api_base = (
            dynamic_api_base
            or mishikallm_params.api_base
            or mishikallm.api_base
            or "https://api.openai.com/"
        )
        # set API KEY
        api_key = (
            dynamic_api_key
            or mishikallm.api_key
            or mishikallm.openai_key
            or get_secret_str("OPENAI_API_KEY")
        )

        await openai_realtime.async_realtime(
            model=model,
            websocket=websocket,
            logging_obj=mishikallm_logging_obj,
            api_base=api_base,
            api_key=api_key,
            client=None,
            timeout=timeout,
        )
    else:
        raise ValueError(f"Unsupported model: {model}")


async def _realtime_health_check(
    model: str,
    custom_llm_provider: str,
    api_key: Optional[str],
    api_base: Optional[str] = None,
    api_version: Optional[str] = None,
):
    """
    Health check for realtime API - tries connection to the realtime API websocket

    Args:
        model: str - model name
        api_base: str - api base
        api_version: Optional[str] - api version
        api_key: str - api key
        custom_llm_provider: str - custom llm provider

    Returns:
        bool - True if connection is successful, False otherwise
    Raises:
        Exception - if the connection is not successful
    """
    import websockets

    url: Optional[str] = None
    if custom_llm_provider == "azure":
        url = azure_realtime._construct_url(
            api_base=api_base or "",
            model=model,
            api_version=api_version or "2024-10-01-preview",
        )
    elif custom_llm_provider == "openai":
        url = openai_realtime._construct_url(
            api_base=api_base or "https://api.openai.com/", model=model
        )
    else:
        raise ValueError(f"Unsupported model: {model}")
    async with websockets.connect(  # type: ignore
        url,
        extra_headers={
            "api-key": api_key,  # type: ignore
        },
    ):
        return True
