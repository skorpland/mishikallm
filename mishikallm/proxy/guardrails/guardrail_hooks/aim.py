# +-------------------------------------------------------------+
#
#           Use Aim Security Guardrails for your LLM calls
#                   https://www.aim.security/
#
# +-------------------------------------------------------------+
import asyncio
import json
import os
from typing import Any, AsyncGenerator, Literal, Optional, Union

from fastapi import HTTPException
from pydantic import BaseModel
from websockets.asyncio.client import ClientConnection, connect

from mishikallm import DualCache
from mishikallm._version import version as mishikallm_version
from mishikallm._logging import verbose_proxy_logger
from mishikallm.integrations.custom_guardrail import CustomGuardrail
from mishikallm.llms.custom_httpx.http_handler import (
    get_async_httpx_client,
    httpxSpecialProvider,
)
from mishikallm.proxy._types import UserAPIKeyAuth
from mishikallm.proxy.proxy_server import StreamingCallbackError
from mishikallm.types.utils import (
    Choices,
    EmbeddingResponse,
    ImageResponse,
    ModelResponse,
    ModelResponseStream,
)


class AimGuardrailMissingSecrets(Exception):
    pass


class AimGuardrail(CustomGuardrail):
    def __init__(
        self, api_key: Optional[str] = None, api_base: Optional[str] = None, **kwargs
    ):
        self.async_handler = get_async_httpx_client(
            llm_provider=httpxSpecialProvider.GuardrailCallback
        )
        self.api_key = api_key or os.environ.get("AIM_API_KEY")
        if not self.api_key:
            msg = (
                "Couldn't get Aim api key, either set the `AIM_API_KEY` in the environment or "
                "pass it as a parameter to the guardrail in the config file"
            )
            raise AimGuardrailMissingSecrets(msg)
        self.api_base = (
            api_base or os.environ.get("AIM_API_BASE") or "https://api.aim.security"
        )
        self.ws_api_base = self.api_base.replace("http://", "ws://").replace(
            "https://", "wss://"
        )
        super().__init__(**kwargs)

    async def async_pre_call_hook(
        self,
        user_api_key_dict: UserAPIKeyAuth,
        cache: DualCache,
        data: dict,
        call_type: Literal[
            "completion",
            "text_completion",
            "embeddings",
            "image_generation",
            "moderation",
            "audio_transcription",
            "pass_through_endpoint",
            "rerank",
        ],
    ) -> Union[Exception, str, dict, None]:
        verbose_proxy_logger.debug("Inside AIM Pre-Call Hook")

        await self.call_aim_guardrail(
            data, hook="pre_call", key_alias=user_api_key_dict.key_alias
        )
        return data

    async def async_moderation_hook(
        self,
        data: dict,
        user_api_key_dict: UserAPIKeyAuth,
        call_type: Literal[
            "completion",
            "embeddings",
            "image_generation",
            "moderation",
            "audio_transcription",
            "responses",
        ],
    ) -> Union[Exception, str, dict, None]:
        verbose_proxy_logger.debug("Inside AIM Moderation Hook")

        await self.call_aim_guardrail(
            data, hook="moderation", key_alias=user_api_key_dict.key_alias
        )
        return data

    async def call_aim_guardrail(
        self, data: dict, hook: str, key_alias: Optional[str]
    ) -> None:
        user_email = data.get("metadata", {}).get("headers", {}).get("x-aim-user-email")
        call_id = data.get("mishikallm_call_id")
        headers = self._build_aim_headers(
            hook=hook,
            key_alias=key_alias,
            user_email=user_email,
            mishikallm_call_id=call_id,
        )
        response = await self.async_handler.post(
            f"{self.api_base}/detect/openai",
            headers=headers,
            json={"messages": data.get("messages", [])},
        )
        response.raise_for_status()
        res = response.json()
        detected = res["detected"]
        verbose_proxy_logger.info(
            "Aim: detected: {detected}, enabled policies: {policies}".format(
                detected=detected,
                policies=list(res["details"].keys()),
            ),
        )
        if detected:
            raise HTTPException(status_code=400, detail=res["detection_message"])

    async def call_aim_guardrail_on_output(
        self, request_data: dict, output: str, hook: str, key_alias: Optional[str]
    ) -> Optional[str]:
        user_email = (
            request_data.get("metadata", {}).get("headers", {}).get("x-aim-user-email")
        )
        call_id = request_data.get("mishikallm_call_id")
        response = await self.async_handler.post(
            f"{self.api_base}/detect/output",
            headers=self._build_aim_headers(
                hook=hook,
                key_alias=key_alias,
                user_email=user_email,
                mishikallm_call_id=call_id,
            ),
            json={"output": output, "messages": request_data.get("messages", [])},
        )
        response.raise_for_status()
        res = response.json()
        detected = res["detected"]
        verbose_proxy_logger.info(
            "Aim: detected: {detected}, enabled policies: {policies}".format(
                detected=detected,
                policies=list(res["details"].keys()),
            ),
        )
        if detected:
            return res["detection_message"]
        return None

    def _build_aim_headers(
        self,
        *,
        hook: str,
        key_alias: Optional[str],
        user_email: Optional[str],
        mishikallm_call_id: Optional[str],
    ):
        """
        A helper function to build the http headers that are required by AIM guardrails.
        """
        return (
            {
                "Authorization": f"Bearer {self.api_key}",
                # Used by Aim to apply only the guardrails that should be applied in a specific request phase.
                "x-aim-mishikallm-hook": hook,
                # Used by Aim to track MishikaLLM version and provide backward compatibility.
                "x-aim-mishikallm-version": mishikallm_version,
            }
            # Used by Aim to track together single call input and output
            | ({"x-aim-mishikallm-call-id": mishikallm_call_id} if mishikallm_call_id else {})
            # Used by Aim to track guardrails violations by user.
            | ({"x-aim-user-email": user_email} if user_email else {})
            | (
                {
                    # Used by Aim apply only the guardrails that are associated with the key alias.
                    "x-aim-mishikallm-key-alias": key_alias,
                }
                if key_alias
                else {}
            )
        )

    async def async_post_call_success_hook(
        self,
        data: dict,
        user_api_key_dict: UserAPIKeyAuth,
        response: Union[Any, ModelResponse, EmbeddingResponse, ImageResponse],
    ) -> Any:
        if (
            isinstance(response, ModelResponse)
            and response.choices
            and isinstance(response.choices[0], Choices)
        ):
            content = response.choices[0].message.content or ""
            detection = await self.call_aim_guardrail_on_output(
                data, content, hook="output", key_alias=user_api_key_dict.key_alias
            )
            if detection:
                raise HTTPException(status_code=400, detail=detection)

    async def async_post_call_streaming_iterator_hook(
        self,
        user_api_key_dict: UserAPIKeyAuth,
        response,
        request_data: dict,
    ) -> AsyncGenerator[ModelResponseStream, None]:
        user_email = (
            request_data.get("metadata", {}).get("headers", {}).get("x-aim-user-email")
        )
        call_id = request_data.get("mishikallm_call_id")
        async with connect(
            f"{self.ws_api_base}/detect/output/ws",
            additional_headers=self._build_aim_headers(
                hook="output",
                key_alias=user_api_key_dict.key_alias,
                user_email=user_email,
                mishikallm_call_id=call_id,
            ),
        ) as websocket:
            sender = asyncio.create_task(
                self.forward_the_stream_to_aim(websocket, response)
            )
            while True:
                result = json.loads(await websocket.recv())
                if verified_chunk := result.get("verified_chunk"):
                    yield ModelResponseStream.model_validate(verified_chunk)
                else:
                    sender.cancel()
                    if result.get("done"):
                        return
                    if blocking_message := result.get("blocking_message"):
                        raise StreamingCallbackError(blocking_message)
                    verbose_proxy_logger.error(
                        f"Unknown message received from AIM: {result}"
                    )
                    return

    async def forward_the_stream_to_aim(
        self,
        websocket: ClientConnection,
        response_iter,
    ) -> None:
        async for chunk in response_iter:
            if isinstance(chunk, BaseModel):
                chunk = chunk.model_dump_json()
            if isinstance(chunk, dict):
                chunk = json.dumps(chunk)
            await websocket.send(chunk)
        await websocket.send(json.dumps({"done": True}))
