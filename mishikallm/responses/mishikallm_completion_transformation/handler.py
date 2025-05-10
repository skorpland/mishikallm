"""
Handler for transforming responses api requests to mishikallm.completion requests
"""

from typing import Any, Coroutine, Optional, Union

import mishikallm
from mishikallm.responses.mishikallm_completion_transformation.streaming_iterator import (
    MishikaLLMCompletionStreamingIterator,
)
from mishikallm.responses.mishikallm_completion_transformation.transformation import (
    MishikaLLMCompletionResponsesConfig,
)
from mishikallm.responses.streaming_iterator import BaseResponsesAPIStreamingIterator
from mishikallm.types.llms.openai import (
    ResponseInputParam,
    ResponsesAPIOptionalRequestParams,
    ResponsesAPIResponse,
)
from mishikallm.types.utils import ModelResponse


class MishikaLLMCompletionTransformationHandler:

    def response_api_handler(
        self,
        model: str,
        input: Union[str, ResponseInputParam],
        responses_api_request: ResponsesAPIOptionalRequestParams,
        custom_llm_provider: Optional[str] = None,
        _is_async: bool = False,
        stream: Optional[bool] = None,
        **kwargs,
    ) -> Union[
        ResponsesAPIResponse,
        BaseResponsesAPIStreamingIterator,
        Coroutine[
            Any, Any, Union[ResponsesAPIResponse, BaseResponsesAPIStreamingIterator]
        ],
    ]:
        mishikallm_completion_request: dict = (
            MishikaLLMCompletionResponsesConfig.transform_responses_api_request_to_chat_completion_request(
                model=model,
                input=input,
                responses_api_request=responses_api_request,
                custom_llm_provider=custom_llm_provider,
                stream=stream,
                **kwargs,
            )
        )

        if _is_async:
            return self.async_response_api_handler(
                mishikallm_completion_request=mishikallm_completion_request,
                request_input=input,
                responses_api_request=responses_api_request,
                **kwargs,
            )

        mishikallm_completion_response: Union[
            ModelResponse, mishikallm.CustomStreamWrapper
        ] = mishikallm.completion(
            **mishikallm_completion_request,
            **kwargs,
        )

        if isinstance(mishikallm_completion_response, ModelResponse):
            responses_api_response: ResponsesAPIResponse = (
                MishikaLLMCompletionResponsesConfig.transform_chat_completion_response_to_responses_api_response(
                    chat_completion_response=mishikallm_completion_response,
                    request_input=input,
                    responses_api_request=responses_api_request,
                )
            )

            return responses_api_response

        elif isinstance(mishikallm_completion_response, mishikallm.CustomStreamWrapper):
            return MishikaLLMCompletionStreamingIterator(
                mishikallm_custom_stream_wrapper=mishikallm_completion_response,
                request_input=input,
                responses_api_request=responses_api_request,
            )

    async def async_response_api_handler(
        self,
        mishikallm_completion_request: dict,
        request_input: Union[str, ResponseInputParam],
        responses_api_request: ResponsesAPIOptionalRequestParams,
        **kwargs,
    ) -> Union[ResponsesAPIResponse, BaseResponsesAPIStreamingIterator]:

        previous_response_id: Optional[str] = responses_api_request.get(
            "previous_response_id"
        )
        if previous_response_id:
            mishikallm_completion_request = await MishikaLLMCompletionResponsesConfig.async_responses_api_session_handler(
                previous_response_id=previous_response_id,
                mishikallm_completion_request=mishikallm_completion_request,
            )

        mishikallm_completion_response: Union[
            ModelResponse, mishikallm.CustomStreamWrapper
        ] = await mishikallm.acompletion(
            **mishikallm_completion_request,
            **kwargs,
        )

        if isinstance(mishikallm_completion_response, ModelResponse):
            responses_api_response: ResponsesAPIResponse = (
                MishikaLLMCompletionResponsesConfig.transform_chat_completion_response_to_responses_api_response(
                    chat_completion_response=mishikallm_completion_response,
                    request_input=request_input,
                    responses_api_request=responses_api_request,
                )
            )

            return responses_api_response

        elif isinstance(mishikallm_completion_response, mishikallm.CustomStreamWrapper):
            return MishikaLLMCompletionStreamingIterator(
                mishikallm_custom_stream_wrapper=mishikallm_completion_response,
                request_input=request_input,
                responses_api_request=responses_api_request,
            )
