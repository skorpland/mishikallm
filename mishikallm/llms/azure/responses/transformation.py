from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple, cast

import httpx

import mishikallm
from mishikallm._logging import verbose_logger
from mishikallm.llms.openai.responses.transformation import OpenAIResponsesAPIConfig
from mishikallm.secret_managers.main import get_secret_str
from mishikallm.types.llms.openai import *
from mishikallm.types.responses.main import *
from mishikallm.types.router import GenericMishikaLLMParams
from mishikallm.utils import _add_path_to_api_base

if TYPE_CHECKING:
    from mishikallm.mishikallm_core_utils.mishikallm_logging import Logging as _MishikaLLMLoggingObj

    MishikaLLMLoggingObj = _MishikaLLMLoggingObj
else:
    MishikaLLMLoggingObj = Any


class AzureOpenAIResponsesAPIConfig(OpenAIResponsesAPIConfig):
    def validate_environment(
        self,
        headers: dict,
        model: str,
        api_key: Optional[str] = None,
    ) -> dict:
        api_key = (
            api_key
            or mishikallm.api_key
            or mishikallm.azure_key
            or get_secret_str("AZURE_OPENAI_API_KEY")
            or get_secret_str("AZURE_API_KEY")
        )

        headers.update(
            {
                "Authorization": f"Bearer {api_key}",
            }
        )
        return headers

    def get_complete_url(
        self,
        api_base: Optional[str],
        mishikallm_params: dict,
    ) -> str:
        """
        Constructs a complete URL for the API request.

        Args:
        - api_base: Base URL, e.g.,
            "https://mishikallm8397336933.openai.azure.com"
            OR
            "https://mishikallm8397336933.openai.azure.com/openai/responses?api-version=2024-05-01-preview"
        - model: Model name.
        - optional_params: Additional query parameters, including "api_version".
        - stream: If streaming is required (optional).

        Returns:
        - A complete URL string, e.g.,
        "https://mishikallm8397336933.openai.azure.com/openai/responses?api-version=2024-05-01-preview"
        """
        api_base = api_base or mishikallm.api_base or get_secret_str("AZURE_API_BASE")
        if api_base is None:
            raise ValueError(
                f"api_base is required for Azure AI Studio. Please set the api_base parameter. Passed `api_base={api_base}`"
            )
        original_url = httpx.URL(api_base)

        # Extract api_version or use default
        api_version = cast(Optional[str], mishikallm_params.get("api_version"))

        # Create a new dictionary with existing params
        query_params = dict(original_url.params)

        # Add api_version if needed
        if "api-version" not in query_params and api_version:
            query_params["api-version"] = api_version

        # Add the path to the base URL
        if "/openai/responses" not in api_base:
            new_url = _add_path_to_api_base(
                api_base=api_base, ending_path="/openai/responses"
            )
        else:
            new_url = api_base

        # Use the new query_params dictionary
        final_url = httpx.URL(new_url).copy_with(params=query_params)

        return str(final_url)

    #########################################################
    ########## DELETE RESPONSE API TRANSFORMATION ##############
    #########################################################
    def _construct_url_for_response_id_in_path(
        self, api_base: str, response_id: str
    ) -> str:
        """
        Constructs a URL for the API request with the response_id in the path.
        """
        from urllib.parse import urlparse, urlunparse

        # Parse the URL to separate its components
        parsed_url = urlparse(api_base)

        # Insert the response_id at the end of the path component
        # Remove trailing slash if present to avoid double slashes
        path = parsed_url.path.rstrip("/")
        new_path = f"{path}/{response_id}"

        # Reconstruct the URL with all original components but with the modified path
        constructed_url = urlunparse(
            (
                parsed_url.scheme,  # http, https
                parsed_url.netloc,  # domain name, port
                new_path,  # path with response_id added
                parsed_url.params,  # parameters
                parsed_url.query,  # query string
                parsed_url.fragment,  # fragment
            )
        )
        return constructed_url

    def transform_delete_response_api_request(
        self,
        response_id: str,
        api_base: str,
        mishikallm_params: GenericMishikaLLMParams,
        headers: dict,
    ) -> Tuple[str, Dict]:
        """
        Transform the delete response API request into a URL and data

        Azure OpenAI API expects the following request:
        - DELETE /openai/responses/{response_id}?api-version=xxx

        This function handles URLs with query parameters by inserting the response_id
        at the correct location (before any query parameters).
        """
        delete_url = self._construct_url_for_response_id_in_path(
            api_base=api_base, response_id=response_id
        )

        data: Dict = {}
        verbose_logger.debug(f"delete response url={delete_url}")
        return delete_url, data

    #########################################################
    ########## GET RESPONSE API TRANSFORMATION ###############
    #########################################################
    def transform_get_response_api_request(
        self,
        response_id: str,
        api_base: str,
        mishikallm_params: GenericMishikaLLMParams,
        headers: dict,
    ) -> Tuple[str, Dict]:
        """
        Transform the get response API request into a URL and data

        OpenAI API expects the following request
        - GET /v1/responses/{response_id}
        """
        get_url = self._construct_url_for_response_id_in_path(
            api_base=api_base, response_id=response_id
        )
        data: Dict = {}
        verbose_logger.debug(f"get response url={get_url}")
        return get_url, data
