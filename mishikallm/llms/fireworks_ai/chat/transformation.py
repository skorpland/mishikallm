import json
import uuid
from typing import Any, List, Literal, Optional, Tuple, Union, cast

import httpx

import mishikallm
from mishikallm.constants import RESPONSE_FORMAT_TOOL_NAME
from mishikallm.mishikallm_core_utils.mishikallm_logging import Logging as MishikaLLMLoggingObj
from mishikallm.mishikallm_core_utils.llm_response_utils.get_headers import (
    get_response_headers,
)
from mishikallm.secret_managers.main import get_secret_str
from mishikallm.types.llms.openai import (
    AllMessageValues,
    ChatCompletionImageObject,
    ChatCompletionToolParam,
    OpenAIChatCompletionToolParam,
)
from mishikallm.types.utils import (
    ChatCompletionMessageToolCall,
    Choices,
    Function,
    Message,
    ModelResponse,
    ProviderSpecificModelInfo,
)

from ...openai.chat.gpt_transformation import OpenAIGPTConfig
from ..common_utils import FireworksAIException


class FireworksAIConfig(OpenAIGPTConfig):
    """
    Reference: https://docs.fireworks.ai/api-reference/post-chatcompletions

    The class `FireworksAIConfig` provides configuration for the Fireworks's Chat Completions API interface. Below are the parameters:
    """

    tools: Optional[list] = None
    tool_choice: Optional[Union[str, dict]] = None
    max_tokens: Optional[int] = None
    temperature: Optional[int] = None
    top_p: Optional[int] = None
    top_k: Optional[int] = None
    frequency_penalty: Optional[int] = None
    presence_penalty: Optional[int] = None
    n: Optional[int] = None
    stop: Optional[Union[str, list]] = None
    response_format: Optional[dict] = None
    user: Optional[str] = None
    logprobs: Optional[int] = None

    # Non OpenAI parameters - Fireworks AI only params
    prompt_truncate_length: Optional[int] = None
    context_length_exceeded_behavior: Optional[Literal["error", "truncate"]] = None

    def __init__(
        self,
        tools: Optional[list] = None,
        tool_choice: Optional[Union[str, dict]] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[int] = None,
        top_p: Optional[int] = None,
        top_k: Optional[int] = None,
        frequency_penalty: Optional[int] = None,
        presence_penalty: Optional[int] = None,
        n: Optional[int] = None,
        stop: Optional[Union[str, list]] = None,
        response_format: Optional[dict] = None,
        user: Optional[str] = None,
        logprobs: Optional[int] = None,
        prompt_truncate_length: Optional[int] = None,
        context_length_exceeded_behavior: Optional[Literal["error", "truncate"]] = None,
    ) -> None:
        locals_ = locals().copy()
        for key, value in locals_.items():
            if key != "self" and value is not None:
                setattr(self.__class__, key, value)

    @classmethod
    def get_config(cls):
        return super().get_config()

    def get_supported_openai_params(self, model: str):
        return [
            "stream",
            "tools",
            "tool_choice",
            "max_completion_tokens",
            "max_tokens",
            "temperature",
            "top_p",
            "top_k",
            "frequency_penalty",
            "presence_penalty",
            "n",
            "stop",
            "response_format",
            "user",
            "logprobs",
            "prompt_truncate_length",
            "context_length_exceeded_behavior",
        ]

    def map_openai_params(
        self,
        non_default_params: dict,
        optional_params: dict,
        model: str,
        drop_params: bool,
    ) -> dict:
        supported_openai_params = self.get_supported_openai_params(model=model)
        is_tools_set = any(
            param == "tools" and value is not None
            for param, value in non_default_params.items()
        )

        for param, value in non_default_params.items():
            if param == "tool_choice":
                if value == "required":
                    # relevant issue: https://github.com/skorpland/mishikallm/issues/4416
                    optional_params["tool_choice"] = "any"
                else:
                    # pass through the value of tool choice
                    optional_params["tool_choice"] = value
            elif param == "response_format":
                if (
                    is_tools_set
                ):  # fireworks ai doesn't support tools and response_format together
                    optional_params = self._add_response_format_to_tools(
                        optional_params=optional_params,
                        value=value,
                        is_response_format_supported=False,
                        enforce_tool_choice=False,  # tools and response_format are both set, don't enforce tool_choice
                    )
                elif "json_schema" in value:
                    optional_params["response_format"] = {
                        "type": "json_object",
                        "schema": value["json_schema"]["schema"],
                    }
                else:
                    optional_params["response_format"] = value
            elif param == "max_completion_tokens":
                optional_params["max_tokens"] = value
            elif param in supported_openai_params:
                if value is not None:
                    optional_params[param] = value

        return optional_params

    def _add_transform_inline_image_block(
        self,
        content: ChatCompletionImageObject,
        model: str,
        disable_add_transform_inline_image_block: Optional[bool],
    ) -> ChatCompletionImageObject:
        """
        Add transform_inline to the image_url (allows non-vision models to parse documents/images/etc.)
        - ignore if model is a vision model
        - ignore if user has disabled this feature
        """
        if (
            "vision" in model or disable_add_transform_inline_image_block
        ):  # allow user to toggle this feature.
            return content
        if isinstance(content["image_url"], str):
            content["image_url"] = f"{content['image_url']}#transform=inline"
        elif isinstance(content["image_url"], dict):
            content["image_url"][
                "url"
            ] = f"{content['image_url']['url']}#transform=inline"
        return content

    def _transform_tools(
        self, tools: List[OpenAIChatCompletionToolParam]
    ) -> List[OpenAIChatCompletionToolParam]:
        for tool in tools:
            if tool.get("type") == "function":
                tool["function"].pop("strict", None)
        return tools

    def _transform_messages_helper(
        self, messages: List[AllMessageValues], model: str, mishikallm_params: dict
    ) -> List[AllMessageValues]:
        """
        Add 'transform=inline' to the url of the image_url
        """
        disable_add_transform_inline_image_block = cast(
            Optional[bool],
            mishikallm_params.get("disable_add_transform_inline_image_block")
            or mishikallm.disable_add_transform_inline_image_block,
        )
        for message in messages:
            if message["role"] == "user":
                _message_content = message.get("content")
                if _message_content is not None and isinstance(_message_content, list):
                    for content in _message_content:
                        if content["type"] == "image_url":
                            content = self._add_transform_inline_image_block(
                                content=content,
                                model=model,
                                disable_add_transform_inline_image_block=disable_add_transform_inline_image_block,
                            )
        return messages

    def get_provider_info(self, model: str) -> ProviderSpecificModelInfo:
        provider_specific_model_info = ProviderSpecificModelInfo(
            supports_function_calling=True,
            supports_prompt_caching=True,  # https://docs.fireworks.ai/guides/prompt-caching
            supports_pdf_input=True,  # via document inlining
            supports_vision=True,  # via document inlining
        )
        return provider_specific_model_info

    def transform_request(
        self,
        model: str,
        messages: List[AllMessageValues],
        optional_params: dict,
        mishikallm_params: dict,
        headers: dict,
    ) -> dict:
        if not model.startswith("accounts/"):
            model = f"accounts/fireworks/models/{model}"
        messages = self._transform_messages_helper(
            messages=messages, model=model, mishikallm_params=mishikallm_params
        )
        if "tools" in optional_params and optional_params["tools"] is not None:
            tools = self._transform_tools(tools=optional_params["tools"])
            optional_params["tools"] = tools
        return super().transform_request(
            model=model,
            messages=messages,
            optional_params=optional_params,
            mishikallm_params=mishikallm_params,
            headers=headers,
        )

    def _handle_message_content_with_tool_calls(
        self,
        message: Message,
        tool_calls: Optional[List[ChatCompletionToolParam]],
    ) -> Message:
        """
        Fireworks AI sends tool calls in the content field instead of tool_calls

        Relevant Issue: https://github.com/skorpland/mishikallm/issues/7209#issuecomment-2813208780
        """
        if (
            tool_calls is not None
            and message.content is not None
            and message.tool_calls is None
        ):
            try:
                function = Function(**json.loads(message.content))
                if function.name != RESPONSE_FORMAT_TOOL_NAME and function.name in [
                    tool["function"]["name"] for tool in tool_calls
                ]:
                    tool_call = ChatCompletionMessageToolCall(
                        function=function, id=str(uuid.uuid4()), type="function"
                    )
                    message.tool_calls = [tool_call]

                    message.content = None
            except Exception:
                pass

        return message

    def transform_response(
        self,
        model: str,
        raw_response: httpx.Response,
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
        ## LOGGING
        logging_obj.post_call(
            input=messages,
            api_key=api_key,
            original_response=raw_response.text,
            additional_args={"complete_input_dict": request_data},
        )

        ## RESPONSE OBJECT
        try:
            completion_response = raw_response.json()
        except Exception as e:
            response_headers = getattr(raw_response, "headers", None)
            raise FireworksAIException(
                message="Unable to get json response - {}, Original Response: {}".format(
                    str(e), raw_response.text
                ),
                status_code=raw_response.status_code,
                headers=response_headers,
            )

        raw_response_headers = dict(raw_response.headers)

        additional_headers = get_response_headers(raw_response_headers)

        response = ModelResponse(**completion_response)

        if response.model is not None:
            response.model = "fireworks_ai/" + response.model

        ## FIREWORKS AI sends tool calls in the content field instead of tool_calls
        for choice in response.choices:
            cast(
                Choices, choice
            ).message = self._handle_message_content_with_tool_calls(
                message=cast(Choices, choice).message,
                tool_calls=optional_params.get("tools", None),
            )

        response._hidden_params = {"additional_headers": additional_headers}

        return response

    def _get_openai_compatible_provider_info(
        self, api_base: Optional[str], api_key: Optional[str]
    ) -> Tuple[Optional[str], Optional[str]]:
        api_base = (
            api_base
            or get_secret_str("FIREWORKS_API_BASE")
            or "https://api.fireworks.ai/inference/v1"
        )  # type: ignore
        dynamic_api_key = api_key or (
            get_secret_str("FIREWORKS_API_KEY")
            or get_secret_str("FIREWORKS_AI_API_KEY")
            or get_secret_str("FIREWORKSAI_API_KEY")
            or get_secret_str("FIREWORKS_AI_TOKEN")
        )
        return api_base, dynamic_api_key

    def get_models(self, api_key: Optional[str] = None, api_base: Optional[str] = None):
        api_base, api_key = self._get_openai_compatible_provider_info(
            api_base=api_base, api_key=api_key
        )
        if api_base is None or api_key is None:
            raise ValueError(
                "FIREWORKS_API_BASE or FIREWORKS_API_KEY is not set. Please set the environment variable, to query Fireworks AI's `/models` endpoint."
            )

        account_id = get_secret_str("FIREWORKS_ACCOUNT_ID")
        if account_id is None:
            raise ValueError(
                "FIREWORKS_ACCOUNT_ID is not set. Please set the environment variable, to query Fireworks AI's `/models` endpoint."
            )

        response = mishikallm.module_level_client.get(
            url=f"{api_base}/v1/accounts/{account_id}/models",
            headers={"Authorization": f"Bearer {api_key}"},
        )

        if response.status_code != 200:
            raise ValueError(
                f"Failed to fetch models from Fireworks AI. Status code: {response.status_code}, Response: {response.json()}"
            )

        models = response.json()["models"]

        return ["fireworks_ai/" + model["name"] for model in models]

    @staticmethod
    def get_api_key(api_key: Optional[str] = None) -> Optional[str]:
        return api_key or (
            get_secret_str("FIREWORKS_API_KEY")
            or get_secret_str("FIREWORKS_AI_API_KEY")
            or get_secret_str("FIREWORKSAI_API_KEY")
            or get_secret_str("FIREWORKS_AI_TOKEN")
        )
