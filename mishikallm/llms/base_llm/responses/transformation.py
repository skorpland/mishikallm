import types
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple, Union

import httpx

from mishikallm.types.llms.openai import (
    ResponseInputParam,
    ResponsesAPIOptionalRequestParams,
    ResponsesAPIResponse,
    ResponsesAPIStreamingResponse,
)
from mishikallm.types.responses.main import *
from mishikallm.types.router import GenericMishikaLLMParams

if TYPE_CHECKING:
    from mishikallm.mishikallm_core_utils.mishikallm_logging import Logging as _MishikaLLMLoggingObj

    from ..chat.transformation import BaseLLMException as _BaseLLMException

    MishikaLLMLoggingObj = _MishikaLLMLoggingObj
    BaseLLMException = _BaseLLMException
else:
    MishikaLLMLoggingObj = Any
    BaseLLMException = Any


class BaseResponsesAPIConfig(ABC):
    def __init__(self):
        pass

    @classmethod
    def get_config(cls):
        return {
            k: v
            for k, v in cls.__dict__.items()
            if not k.startswith("__")
            and not k.startswith("_abc")
            and not isinstance(
                v,
                (
                    types.FunctionType,
                    types.BuiltinFunctionType,
                    classmethod,
                    staticmethod,
                ),
            )
            and v is not None
        }

    @abstractmethod
    def get_supported_openai_params(self, model: str) -> list:
        pass

    @abstractmethod
    def map_openai_params(
        self,
        response_api_optional_params: ResponsesAPIOptionalRequestParams,
        model: str,
        drop_params: bool,
    ) -> Dict:
        pass

    @abstractmethod
    def validate_environment(
        self,
        headers: dict,
        model: str,
        api_key: Optional[str] = None,
    ) -> dict:
        return {}

    @abstractmethod
    def get_complete_url(
        self,
        api_base: Optional[str],
        mishikallm_params: dict,
    ) -> str:
        """
        OPTIONAL

        Get the complete url for the request

        Some providers need `model` in `api_base`
        """
        if api_base is None:
            raise ValueError("api_base is required")
        return api_base

    @abstractmethod
    def transform_responses_api_request(
        self,
        model: str,
        input: Union[str, ResponseInputParam],
        response_api_optional_request_params: Dict,
        mishikallm_params: GenericMishikaLLMParams,
        headers: dict,
    ) -> Dict:
        pass

    @abstractmethod
    def transform_response_api_response(
        self,
        model: str,
        raw_response: httpx.Response,
        logging_obj: MishikaLLMLoggingObj,
    ) -> ResponsesAPIResponse:
        pass

    @abstractmethod
    def transform_streaming_response(
        self,
        model: str,
        parsed_chunk: dict,
        logging_obj: MishikaLLMLoggingObj,
    ) -> ResponsesAPIStreamingResponse:
        """
        Transform a parsed streaming response chunk into a ResponsesAPIStreamingResponse
        """
        pass

    #########################################################
    ########## DELETE RESPONSE API TRANSFORMATION ##############
    #########################################################
    @abstractmethod
    def transform_delete_response_api_request(
        self,
        response_id: str,
        api_base: str,
        mishikallm_params: GenericMishikaLLMParams,
        headers: dict,
    ) -> Tuple[str, Dict]:
        pass

    @abstractmethod
    def transform_delete_response_api_response(
        self,
        raw_response: httpx.Response,
        logging_obj: MishikaLLMLoggingObj,
    ) -> DeleteResponseResult:
        pass

    #########################################################
    ########## END DELETE RESPONSE API TRANSFORMATION #######
    #########################################################

    #########################################################
    ########## GET RESPONSE API TRANSFORMATION ###############
    #########################################################
    @abstractmethod
    def transform_get_response_api_request(
        self,
        response_id: str,
        api_base: str,
        mishikallm_params: GenericMishikaLLMParams,
        headers: dict,
    ) -> Tuple[str, Dict]:
        pass
    
    @abstractmethod
    def transform_get_response_api_response(
        self,
        raw_response: httpx.Response,
        logging_obj: MishikaLLMLoggingObj,
    ) -> ResponsesAPIResponse:
        pass

    #########################################################
    ########## END GET RESPONSE API TRANSFORMATION ##########
    #########################################################
    
    def get_error_class(
        self, error_message: str, status_code: int, headers: Union[dict, httpx.Headers]
    ) -> BaseLLMException:
        from ..chat.transformation import BaseLLMException

        raise BaseLLMException(
            status_code=status_code,
            message=error_message,
            headers=headers,
        )

    def should_fake_stream(
        self,
        model: Optional[str],
        stream: Optional[bool],
        custom_llm_provider: Optional[str] = None,
    ) -> bool:
        """Returns True if mishikallm should fake a stream for the given model and stream value"""
        return False
