import ssl
from enum import Enum
from typing import Union


class httpxSpecialProvider(str, Enum):
    """
    Httpx Clients can be created for these mishikallm internal providers

    Example:
    - langsmith logging would need a custom async httpx client
    - pass through endpoint would need a custom async httpx client
    """

    LoggingCallback = "logging_callback"
    GuardrailCallback = "guardrail_callback"
    Caching = "caching"
    Oauth2Check = "oauth2_check"
    SecretManager = "secret_manager"
    PassThroughEndpoint = "pass_through_endpoint"
    PromptFactory = "prompt_factory"
    SSO_HANDLER = "sso_handler"


VerifyTypes = Union[str, bool, ssl.SSLContext]
