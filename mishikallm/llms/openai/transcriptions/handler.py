from typing import Optional, Union

import httpx
from openai import AsyncOpenAI, OpenAI
from pydantic import BaseModel

import mishikallm
from mishikallm.mishikallm_core_utils.audio_utils.utils import get_audio_file_name
from mishikallm.mishikallm_core_utils.mishikallm_logging import Logging as MishikaLLMLoggingObj
from mishikallm.llms.base_llm.audio_transcription.transformation import (
    BaseAudioTranscriptionConfig,
)
from mishikallm.types.utils import FileTypes
from mishikallm.utils import (
    TranscriptionResponse,
    convert_to_model_response_object,
    extract_duration_from_srt_or_vtt,
)

from ..openai import OpenAIChatCompletion


class OpenAIAudioTranscription(OpenAIChatCompletion):
    # Audio Transcriptions
    async def make_openai_audio_transcriptions_request(
        self,
        openai_aclient: AsyncOpenAI,
        data: dict,
        timeout: Union[float, httpx.Timeout],
    ):
        """
        Helper to:
        - call openai_aclient.audio.transcriptions.with_raw_response when mishikallm.return_response_headers is True
        - call openai_aclient.audio.transcriptions.create by default
        """
        try:
            raw_response = (
                await openai_aclient.audio.transcriptions.with_raw_response.create(
                    **data, timeout=timeout
                )
            )  # type: ignore
            headers = dict(raw_response.headers)
            response = raw_response.parse()

            return headers, response
        except Exception as e:
            raise e

    def make_sync_openai_audio_transcriptions_request(
        self,
        openai_client: OpenAI,
        data: dict,
        timeout: Union[float, httpx.Timeout],
    ):
        """
        Helper to:
        - call openai_aclient.audio.transcriptions.with_raw_response when mishikallm.return_response_headers is True
        - call openai_aclient.audio.transcriptions.create by default
        """
        try:
            if mishikallm.return_response_headers is True:
                raw_response = (
                    openai_client.audio.transcriptions.with_raw_response.create(
                        **data, timeout=timeout
                    )
                )  # type: ignore
                headers = dict(raw_response.headers)
                response = raw_response.parse()
                return headers, response
            else:
                response = openai_client.audio.transcriptions.create(**data, timeout=timeout)  # type: ignore
                return None, response
        except Exception as e:
            raise e

    def audio_transcriptions(
        self,
        model: str,
        audio_file: FileTypes,
        optional_params: dict,
        mishikallm_params: dict,
        model_response: TranscriptionResponse,
        timeout: float,
        max_retries: int,
        logging_obj: MishikaLLMLoggingObj,
        api_key: Optional[str],
        api_base: Optional[str],
        client=None,
        atranscription: bool = False,
        provider_config: Optional[BaseAudioTranscriptionConfig] = None,
    ) -> TranscriptionResponse:
        """
        Handle audio transcription request
        """
        if provider_config is not None:
            data = provider_config.transform_audio_transcription_request(
                model=model,
                audio_file=audio_file,
                optional_params=optional_params,
                mishikallm_params=mishikallm_params,
            )

            if isinstance(data, bytes):
                raise ValueError("OpenAI transformation route requires a dict")
        else:
            data = {"model": model, "file": audio_file, **optional_params}

        if atranscription is True:
            return self.async_audio_transcriptions(  # type: ignore
                audio_file=audio_file,
                data=data,
                model_response=model_response,
                timeout=timeout,
                api_key=api_key,
                api_base=api_base,
                client=client,
                max_retries=max_retries,
                logging_obj=logging_obj,
            )

        openai_client: OpenAI = self._get_openai_client(  # type: ignore
            is_async=False,
            api_key=api_key,
            api_base=api_base,
            timeout=timeout,
            max_retries=max_retries,
            client=client,
        )

        ## LOGGING
        logging_obj.pre_call(
            input=None,
            api_key=openai_client.api_key,
            additional_args={
                "api_base": openai_client._base_url._uri_reference,
                "atranscription": True,
                "complete_input_dict": data,
            },
        )
        _, response = self.make_sync_openai_audio_transcriptions_request(
            openai_client=openai_client,
            data=data,
            timeout=timeout,
        )

        if isinstance(response, BaseModel):
            stringified_response = response.model_dump()
        else:
            stringified_response = TranscriptionResponse(text=response).model_dump()

        ## LOGGING
        logging_obj.post_call(
            input=get_audio_file_name(audio_file),
            api_key=api_key,
            additional_args={"complete_input_dict": data},
            original_response=stringified_response,
        )
        hidden_params = {"model": "whisper-1", "custom_llm_provider": "openai"}
        final_response: TranscriptionResponse = convert_to_model_response_object(response_object=stringified_response, model_response_object=model_response, hidden_params=hidden_params, response_type="audio_transcription")  # type: ignore
        return final_response

    async def async_audio_transcriptions(
        self,
        audio_file: FileTypes,
        data: dict,
        model_response: TranscriptionResponse,
        timeout: float,
        logging_obj: MishikaLLMLoggingObj,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        client=None,
        max_retries=None,
    ):
        try:
            openai_aclient: AsyncOpenAI = self._get_openai_client(  # type: ignore
                is_async=True,
                api_key=api_key,
                api_base=api_base,
                timeout=timeout,
                max_retries=max_retries,
                client=client,
            )

            ## LOGGING
            logging_obj.pre_call(
                input=None,
                api_key=openai_aclient.api_key,
                additional_args={
                    "api_base": openai_aclient._base_url._uri_reference,
                    "atranscription": True,
                    "complete_input_dict": data,
                },
            )
            headers, response = await self.make_openai_audio_transcriptions_request(
                openai_aclient=openai_aclient,
                data=data,
                timeout=timeout,
            )
            logging_obj.model_call_details["response_headers"] = headers
            if isinstance(response, BaseModel):
                stringified_response = response.model_dump()
            else:
                duration = extract_duration_from_srt_or_vtt(response)
                stringified_response = TranscriptionResponse(text=response).model_dump()
                stringified_response["duration"] = duration
            ## LOGGING
            logging_obj.post_call(
                input=get_audio_file_name(audio_file),
                api_key=api_key,
                additional_args={"complete_input_dict": data},
                original_response=stringified_response,
            )
            hidden_params = {"model": "whisper-1", "custom_llm_provider": "openai"}
            return convert_to_model_response_object(response_object=stringified_response, model_response_object=model_response, hidden_params=hidden_params, response_type="audio_transcription")  # type: ignore
        except Exception as e:
            ## LOGGING
            logging_obj.post_call(
                input=input,
                api_key=api_key,
                original_response=str(e),
            )
            raise e
