import json
from datetime import datetime
from typing import TYPE_CHECKING, Any, List, Optional, Union

import httpx

import mishikallm
from mishikallm._logging import verbose_proxy_logger
from mishikallm.mishikallm_core_utils.mishikallm_logging import Logging as MishikaLLMLoggingObj
from mishikallm.mishikallm_core_utils.mishikallm_logging import (
    get_standard_logging_object_payload,
)
from mishikallm.llms.base_llm.chat.transformation import BaseConfig
from mishikallm.proxy._types import PassThroughEndpointLoggingTypedDict
from mishikallm.proxy.auth.auth_utils import get_end_user_id_from_request_body
from mishikallm.types.passthrough_endpoints.pass_through_endpoints import (
    PassthroughStandardLoggingPayload,
)
from mishikallm.types.utils import LlmProviders, ModelResponse, TextCompletionResponse

if TYPE_CHECKING:
    from ..success_handler import PassThroughEndpointLogging
    from ..types import EndpointType
else:
    PassThroughEndpointLogging = Any
    EndpointType = Any

from abc import ABC, abstractmethod


class BasePassthroughLoggingHandler(ABC):
    @property
    @abstractmethod
    def llm_provider_name(self) -> LlmProviders:
        pass

    @abstractmethod
    def get_provider_config(self, model: str) -> BaseConfig:
        pass

    def passthrough_chat_handler(
        self,
        httpx_response: httpx.Response,
        response_body: dict,
        logging_obj: MishikaLLMLoggingObj,
        url_route: str,
        result: str,
        start_time: datetime,
        end_time: datetime,
        cache_hit: bool,
        request_body: dict,
        **kwargs,
    ) -> PassThroughEndpointLoggingTypedDict:
        """
        Transforms LLM response to OpenAI response, generates a standard logging object so downstream logging can be handled
        """
        model = request_body.get("model", response_body.get("model", ""))
        provider_config = self.get_provider_config(model=model)
        mishikallm_model_response: ModelResponse = provider_config.transform_response(
            raw_response=httpx_response,
            model_response=mishikallm.ModelResponse(),
            model=model,
            messages=[],
            logging_obj=logging_obj,
            optional_params={},
            api_key="",
            request_data={},
            encoding=mishikallm.encoding,
            json_mode=False,
            mishikallm_params={},
        )

        kwargs = self._create_response_logging_payload(
            mishikallm_model_response=mishikallm_model_response,
            model=model,
            kwargs=kwargs,
            start_time=start_time,
            end_time=end_time,
            logging_obj=logging_obj,
        )

        return {
            "result": mishikallm_model_response,
            "kwargs": kwargs,
        }

    def _get_user_from_metadata(
        self,
        passthrough_logging_payload: PassthroughStandardLoggingPayload,
    ) -> Optional[str]:
        request_body = passthrough_logging_payload.get("request_body")
        if request_body:
            return get_end_user_id_from_request_body(request_body)
        return None

    def _create_response_logging_payload(
        self,
        mishikallm_model_response: Union[ModelResponse, TextCompletionResponse],
        model: str,
        kwargs: dict,
        start_time: datetime,
        end_time: datetime,
        logging_obj: MishikaLLMLoggingObj,
    ) -> dict:
        """
        Create the standard logging object for Generic LLM passthrough

        handles streaming and non-streaming responses
        """

        try:
            response_cost = mishikallm.completion_cost(
                completion_response=mishikallm_model_response,
                model=model,
            )

            kwargs["response_cost"] = response_cost
            kwargs["model"] = model
            passthrough_logging_payload: Optional[PassthroughStandardLoggingPayload] = (  # type: ignore
                kwargs.get("passthrough_logging_payload")
            )
            if passthrough_logging_payload:
                user = self._get_user_from_metadata(
                    passthrough_logging_payload=passthrough_logging_payload,
                )
                if user:
                    kwargs.setdefault("mishikallm_params", {})
                    kwargs["mishikallm_params"].update(
                        {"proxy_server_request": {"body": {"user": user}}}
                    )

            # Make standard logging object for Anthropic
            standard_logging_object = get_standard_logging_object_payload(
                kwargs=kwargs,
                init_response_obj=mishikallm_model_response,
                start_time=start_time,
                end_time=end_time,
                logging_obj=logging_obj,
                status="success",
            )

            # pretty print standard logging object
            verbose_proxy_logger.debug(
                "standard_logging_object= %s",
                json.dumps(standard_logging_object, indent=4),
            )
            kwargs["standard_logging_object"] = standard_logging_object

            # set mishikallm_call_id to logging response object
            mishikallm_model_response.id = logging_obj.mishikallm_call_id
            mishikallm_model_response.model = model
            logging_obj.model_call_details["model"] = model
            return kwargs
        except Exception as e:
            verbose_proxy_logger.exception(
                "Error creating LLM passthrough response logging payload: %s", e
            )
            return kwargs

    @abstractmethod
    def _build_complete_streaming_response(
        self,
        all_chunks: List[str],
        mishikallm_logging_obj: MishikaLLMLoggingObj,
        model: str,
    ) -> Optional[Union[ModelResponse, TextCompletionResponse]]:
        """
        Builds complete response from raw chunks

        - Converts str chunks to generic chunks
        - Converts generic chunks to mishikallm chunks (OpenAI format)
        - Builds complete response from mishikallm chunks
        """
        pass

    def _handle_logging_llm_collected_chunks(
        self,
        mishikallm_logging_obj: MishikaLLMLoggingObj,
        passthrough_success_handler_obj: PassThroughEndpointLogging,
        url_route: str,
        request_body: dict,
        endpoint_type: EndpointType,
        start_time: datetime,
        all_chunks: List[str],
        end_time: datetime,
    ) -> PassThroughEndpointLoggingTypedDict:
        """
        Takes raw chunks from Anthropic passthrough endpoint and logs them in mishikallm callbacks

        - Builds complete response from chunks
        - Creates standard logging object
        - Logs in mishikallm callbacks
        """

        model = request_body.get("model", "")
        complete_streaming_response = self._build_complete_streaming_response(
            all_chunks=all_chunks,
            mishikallm_logging_obj=mishikallm_logging_obj,
            model=model,
        )
        if complete_streaming_response is None:
            verbose_proxy_logger.error(
                "Unable to build complete streaming response for Anthropic passthrough endpoint, not logging..."
            )
            return {
                "result": None,
                "kwargs": {},
            }
        kwargs = self._create_response_logging_payload(
            mishikallm_model_response=complete_streaming_response,
            model=model,
            kwargs={},
            start_time=start_time,
            end_time=end_time,
            logging_obj=mishikallm_logging_obj,
        )

        return {
            "result": complete_streaming_response,
            "kwargs": kwargs,
        }
