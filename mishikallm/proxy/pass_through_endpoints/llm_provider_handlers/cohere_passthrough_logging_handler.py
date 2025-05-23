from typing import List, Optional, Union

from mishikallm import stream_chunk_builder
from mishikallm.mishikallm_core_utils.mishikallm_logging import Logging as MishikaLLMLoggingObj
from mishikallm.mishikallm_core_utils.streaming_handler import CustomStreamWrapper
from mishikallm.llms.base_llm.chat.transformation import BaseConfig
from mishikallm.llms.cohere.chat.v2_transformation import CohereV2ChatConfig
from mishikallm.llms.cohere.common_utils import (
    ModelResponseIterator as CohereModelResponseIterator,
)
from mishikallm.types.utils import LlmProviders, ModelResponse, TextCompletionResponse

from .base_passthrough_logging_handler import BasePassthroughLoggingHandler


class CoherePassthroughLoggingHandler(BasePassthroughLoggingHandler):
    @property
    def llm_provider_name(self) -> LlmProviders:
        return LlmProviders.COHERE

    def get_provider_config(self, model: str) -> BaseConfig:
        return CohereV2ChatConfig()

    def _build_complete_streaming_response(
        self,
        all_chunks: List[str],
        mishikallm_logging_obj: MishikaLLMLoggingObj,
        model: str,
    ) -> Optional[Union[ModelResponse, TextCompletionResponse]]:
        cohere_model_response_iterator = CohereModelResponseIterator(
            streaming_response=None,
            sync_stream=False,
        )
        mishikallm_custom_stream_wrapper = CustomStreamWrapper(
            completion_stream=cohere_model_response_iterator,
            model=model,
            logging_obj=mishikallm_logging_obj,
            custom_llm_provider="cohere",
        )
        all_openai_chunks = []
        for _chunk_str in all_chunks:
            try:
                generic_chunk = (
                    cohere_model_response_iterator.convert_str_chunk_to_generic_chunk(
                        chunk=_chunk_str
                    )
                )
                mishikallm_chunk = mishikallm_custom_stream_wrapper.chunk_creator(
                    chunk=generic_chunk
                )
                if mishikallm_chunk is not None:
                    all_openai_chunks.append(mishikallm_chunk)
            except (StopIteration, StopAsyncIteration):
                break
        complete_streaming_response = stream_chunk_builder(chunks=all_openai_chunks)
        return complete_streaming_response
