"""
Support for o1/o3 model family 

https://platform.openai.com/docs/guides/reasoning

Translations handled by MishikaLLM:
- modalities: image => drop param (if user opts in to dropping param)  
- role: system ==> translate to role 'user' 
- streaming => faked by MishikaLLM 
- Tools, response_format =>  drop param (if user opts in to dropping param) 
- Logprobs => drop param (if user opts in to dropping param) 
"""

from typing import List, Optional

import mishikallm
from mishikallm import verbose_logger
from mishikallm.mishikallm_core_utils.get_llm_provider_logic import get_llm_provider
from mishikallm.types.llms.openai import AllMessageValues, ChatCompletionUserMessage
from mishikallm.utils import (
    supports_function_calling,
    supports_parallel_function_calling,
    supports_response_schema,
    supports_system_messages,
)

from .gpt_transformation import OpenAIGPTConfig


class OpenAIOSeriesConfig(OpenAIGPTConfig):
    """
    Reference: https://platform.openai.com/docs/guides/reasoning
    """

    @classmethod
    def get_config(cls):
        return super().get_config()

    def translate_developer_role_to_system_role(
        self, messages: List[AllMessageValues]
    ) -> List[AllMessageValues]:
        """
        O-series models support `developer` role.
        """
        return messages

    def get_supported_openai_params(self, model: str) -> list:
        """
        Get the supported OpenAI params for the given model

        """

        all_openai_params = super().get_supported_openai_params(model=model)
        non_supported_params = [
            "logprobs",
            "top_p",
            "presence_penalty",
            "frequency_penalty",
            "top_logprobs",
        ]

        o_series_only_param = ["reasoning_effort"]

        all_openai_params.extend(o_series_only_param)

        try:
            model, custom_llm_provider, api_base, api_key = get_llm_provider(
                model=model
            )
        except Exception:
            verbose_logger.debug(
                f"Unable to infer model provider for model={model}, defaulting to openai for o1 supported param check"
            )
            custom_llm_provider = "openai"

        _supports_function_calling = supports_function_calling(
            model, custom_llm_provider
        )
        _supports_response_schema = supports_response_schema(model, custom_llm_provider)
        _supports_parallel_tool_calls = supports_parallel_function_calling(
            model, custom_llm_provider
        )

        if not _supports_function_calling:
            non_supported_params.append("tools")
            non_supported_params.append("tool_choice")
            non_supported_params.append("function_call")
            non_supported_params.append("functions")

        if not _supports_parallel_tool_calls:
            non_supported_params.append("parallel_tool_calls")

        if not _supports_response_schema:
            non_supported_params.append("response_format")

        return [
            param for param in all_openai_params if param not in non_supported_params
        ]

    def map_openai_params(
        self,
        non_default_params: dict,
        optional_params: dict,
        model: str,
        drop_params: bool,
    ):
        if "max_tokens" in non_default_params:
            optional_params["max_completion_tokens"] = non_default_params.pop(
                "max_tokens"
            )
        if "temperature" in non_default_params:
            temperature_value: Optional[float] = non_default_params.pop("temperature")
            if temperature_value is not None:
                if temperature_value == 1:
                    optional_params["temperature"] = temperature_value
                else:
                    ## UNSUPPORTED TOOL CHOICE VALUE
                    if mishikallm.drop_params is True or drop_params is True:
                        pass
                    else:
                        raise mishikallm.utils.UnsupportedParamsError(
                            message="O-series models don't support temperature={}. Only temperature=1 is supported. To drop unsupported openai params from the call, set `mishikallm.drop_params = True`".format(
                                temperature_value
                            ),
                            status_code=400,
                        )

        return super()._map_openai_params(
            non_default_params, optional_params, model, drop_params
        )

    def is_model_o_series_model(self, model: str) -> bool:
        if model in mishikallm.open_ai_chat_completion_models and (
            "o1" in model
            or "o3" in model
            or "o4"
            in model  # [TODO] make this a more generic check (e.g. using `openai-o-series` as provider like gemini)
        ):
            return True
        return False

    def _transform_messages(
        self, messages: List[AllMessageValues], model: str
    ) -> List[AllMessageValues]:
        """
        Handles limitations of O-1 model family.
        - modalities: image => drop param (if user opts in to dropping param)
        - role: system ==> translate to role 'user'
        """
        _supports_system_messages = supports_system_messages(model, "openai")
        for i, message in enumerate(messages):
            if message["role"] == "system" and not _supports_system_messages:
                new_message = ChatCompletionUserMessage(
                    content=message["content"], role="user"
                )
                messages[i] = new_message  # Replace the old message with the new one

        messages = super()._transform_messages(messages, model)
        return messages
