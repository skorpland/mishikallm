# What is this?
## API Handler for calling Vertex AI Partner Models
from enum import Enum
from typing import Callable, Optional, Union

import httpx  # type: ignore

import mishikallm
from mishikallm import LlmProviders
from mishikallm.utils import ModelResponse

from ...custom_httpx.llm_http_handler import BaseLLMHTTPHandler
from ..vertex_llm_base import VertexBase

base_llm_http_handler = BaseLLMHTTPHandler()


class VertexPartnerProvider(str, Enum):
    mistralai = "mistralai"
    llama = "llama"
    ai21 = "ai21"
    claude = "claude"


class VertexAIError(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        self.request = httpx.Request(
            method="POST", url=" https://cloud.google.com/vertex-ai/"
        )
        self.response = httpx.Response(status_code=status_code, request=self.request)
        super().__init__(
            self.message
        )  # Call the base class constructor with the parameters it needs


def create_vertex_url(
    vertex_location: str,
    vertex_project: str,
    partner: VertexPartnerProvider,
    stream: Optional[bool],
    model: str,
    api_base: Optional[str] = None,
) -> str:
    """Return the base url for the vertex partner models"""
    if partner == VertexPartnerProvider.llama:
        return f"https://{vertex_location}-aiplatform.googleapis.com/v1beta1/projects/{vertex_project}/locations/{vertex_location}/endpoints/openapi/chat/completions"
    elif partner == VertexPartnerProvider.mistralai:
        if stream:
            return f"https://{vertex_location}-aiplatform.googleapis.com/v1/projects/{vertex_project}/locations/{vertex_location}/publishers/mistralai/models/{model}:streamRawPredict"
        else:
            return f"https://{vertex_location}-aiplatform.googleapis.com/v1/projects/{vertex_project}/locations/{vertex_location}/publishers/mistralai/models/{model}:rawPredict"
    elif partner == VertexPartnerProvider.ai21:
        if stream:
            return f"https://{vertex_location}-aiplatform.googleapis.com/v1beta1/projects/{vertex_project}/locations/{vertex_location}/publishers/ai21/models/{model}:streamRawPredict"
        else:
            return f"https://{vertex_location}-aiplatform.googleapis.com/v1beta1/projects/{vertex_project}/locations/{vertex_location}/publishers/ai21/models/{model}:rawPredict"
    elif partner == VertexPartnerProvider.claude:
        if stream:
            return f"https://{vertex_location}-aiplatform.googleapis.com/v1/projects/{vertex_project}/locations/{vertex_location}/publishers/anthropic/models/{model}:streamRawPredict"
        else:
            return f"https://{vertex_location}-aiplatform.googleapis.com/v1/projects/{vertex_project}/locations/{vertex_location}/publishers/anthropic/models/{model}:rawPredict"


class VertexAIPartnerModels(VertexBase):
    def __init__(self) -> None:
        pass

    def completion(
        self,
        model: str,
        messages: list,
        model_response: ModelResponse,
        print_verbose: Callable,
        encoding,
        logging_obj,
        api_base: Optional[str],
        optional_params: dict,
        custom_prompt_dict: dict,
        headers: Optional[dict],
        timeout: Union[float, httpx.Timeout],
        mishikallm_params: dict,
        vertex_project=None,
        vertex_location=None,
        vertex_credentials=None,
        logger_fn=None,
        acompletion: bool = False,
        client=None,
    ):
        try:
            import vertexai

            from mishikallm.llms.anthropic.chat import AnthropicChatCompletion
            from mishikallm.llms.codestral.completion.handler import (
                CodestralTextCompletion,
            )
            from mishikallm.llms.openai_like.chat.handler import OpenAILikeChatHandler
            from mishikallm.llms.vertex_ai.gemini.vertex_and_google_ai_studio_gemini import (
                VertexLLM,
            )
        except Exception as e:
            raise VertexAIError(
                status_code=400,
                message=f"""vertexai import failed please run `pip install -U "google-cloud-aiplatform>=1.38"`. Got error: {e}""",
            )

        if not (
            hasattr(vertexai, "preview") or hasattr(vertexai.preview, "language_models")
        ):
            raise VertexAIError(
                status_code=400,
                message="""Upgrade vertex ai. Run `pip install "google-cloud-aiplatform>=1.38"`""",
            )
        try:
            vertex_httpx_logic = VertexLLM()

            access_token, project_id = vertex_httpx_logic._ensure_access_token(
                credentials=vertex_credentials,
                project_id=vertex_project,
                custom_llm_provider="vertex_ai",
            )

            openai_like_chat_completions = OpenAILikeChatHandler()
            codestral_fim_completions = CodestralTextCompletion()
            anthropic_chat_completions = AnthropicChatCompletion()

            ## CONSTRUCT API BASE
            stream: bool = optional_params.get("stream", False) or False

            optional_params["stream"] = stream

            if "llama" in model:
                partner = VertexPartnerProvider.llama
            elif "mistral" in model or "codestral" in model:
                partner = VertexPartnerProvider.mistralai
            elif "jamba" in model:
                partner = VertexPartnerProvider.ai21
            elif "claude" in model:
                partner = VertexPartnerProvider.claude

            default_api_base = create_vertex_url(
                vertex_location=vertex_location or "us-central1",
                vertex_project=vertex_project or project_id,
                partner=partner,  # type: ignore
                stream=stream,
                model=model,
            )

            if len(default_api_base.split(":")) > 1:
                endpoint = default_api_base.split(":")[-1]
            else:
                endpoint = ""

            _, api_base = self._check_custom_proxy(
                api_base=api_base,
                custom_llm_provider="vertex_ai",
                gemini_api_key=None,
                endpoint=endpoint,
                stream=stream,
                auth_header=None,
                url=default_api_base,
            )

            if "codestral" in model or "mistral" in model:
                model = model.split("@")[0]

            if "codestral" in model and mishikallm_params.get("text_completion") is True:
                optional_params["model"] = model
                text_completion_model_response = mishikallm.TextCompletionResponse(
                    stream=stream
                )
                return codestral_fim_completions.completion(
                    model=model,
                    messages=messages,
                    api_base=api_base,
                    api_key=access_token,
                    custom_prompt_dict=custom_prompt_dict,
                    model_response=text_completion_model_response,
                    print_verbose=print_verbose,
                    logging_obj=logging_obj,
                    optional_params=optional_params,
                    acompletion=acompletion,
                    mishikallm_params=mishikallm_params,
                    logger_fn=logger_fn,
                    timeout=timeout,
                    encoding=encoding,
                )
            elif "claude" in model:
                if headers is None:
                    headers = {}
                headers.update({"Authorization": "Bearer {}".format(access_token)})

                optional_params.update(
                    {
                        "anthropic_version": "vertex-2023-10-16",
                        "is_vertex_request": True,
                    }
                )

                return anthropic_chat_completions.completion(
                    model=model,
                    messages=messages,
                    api_base=api_base,
                    acompletion=acompletion,
                    custom_prompt_dict=mishikallm.custom_prompt_dict,
                    model_response=model_response,
                    print_verbose=print_verbose,
                    optional_params=optional_params,
                    mishikallm_params=mishikallm_params,
                    logger_fn=logger_fn,
                    encoding=encoding,  # for calculating input/output tokens
                    api_key=access_token,
                    logging_obj=logging_obj,
                    headers=headers,
                    timeout=timeout,
                    client=client,
                    custom_llm_provider=LlmProviders.VERTEX_AI.value,
                )
            elif "llama" in model:
                return base_llm_http_handler.completion(
                    model=model,
                    stream=stream,
                    messages=messages,
                    acompletion=acompletion,
                    api_base=api_base,
                    model_response=model_response,
                    optional_params=optional_params,
                    mishikallm_params=mishikallm_params,
                    custom_llm_provider="vertex_ai",
                    timeout=timeout,
                    headers=headers,
                    encoding=encoding,
                    api_key=access_token,
                    logging_obj=logging_obj,  # model call logging done inside the class as we make need to modify I/O to fit aleph alpha's requirements
                    client=client,
                )
            return openai_like_chat_completions.completion(
                model=model,
                messages=messages,
                api_base=api_base,
                api_key=access_token,
                custom_prompt_dict=custom_prompt_dict,
                model_response=model_response,
                print_verbose=print_verbose,
                logging_obj=logging_obj,
                optional_params=optional_params,
                acompletion=acompletion,
                mishikallm_params=mishikallm_params,
                logger_fn=logger_fn,
                client=client,
                timeout=timeout,
                encoding=encoding,
                custom_llm_provider="vertex_ai",
                custom_endpoint=True,
            )

        except Exception as e:
            if hasattr(e, "status_code"):
                raise e
            raise VertexAIError(status_code=500, message=str(e))
