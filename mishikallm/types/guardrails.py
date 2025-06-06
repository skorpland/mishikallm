from enum import Enum
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union

from pydantic import BaseModel, ConfigDict, Field, SecretStr
from typing_extensions import Required, TypedDict

"""
Pydantic object defining how to set guardrails on mishikallm proxy

guardrails:
  - guardrail_name: "bedrock-pre-guard"
    mishikallm_params:
      guardrail: bedrock  # supported values: "aporia", "bedrock", "lakera"
      mode: "during_call"
      guardrailIdentifier: ff6ujrregl1q
      guardrailVersion: "DRAFT"
      default_on: true
"""


class SupportedGuardrailIntegrations(Enum):
    APORIA = "aporia"
    BEDROCK = "bedrock"
    GURDRAILS_AI = "guardrails_ai"
    LAKERA = "lakera"
    PRESIDIO = "presidio"
    HIDE_SECRETS = "hide-secrets"
    AIM = "aim"


class Role(Enum):
    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"


default_roles = [Role.SYSTEM, Role.ASSISTANT, Role.USER]


class GuardrailItemSpec(TypedDict, total=False):
    callbacks: Required[List[str]]
    default_on: bool
    logging_only: Optional[bool]
    enabled_roles: Optional[List[Role]]
    callback_args: Dict[str, Dict]


class GuardrailItem(BaseModel):
    callbacks: List[str]
    default_on: bool
    logging_only: Optional[bool]
    guardrail_name: str
    callback_args: Dict[str, Dict]
    enabled_roles: Optional[List[Role]]

    model_config = ConfigDict(use_enum_values=True)

    def __init__(
        self,
        callbacks: List[str],
        guardrail_name: str,
        default_on: bool = False,
        logging_only: Optional[bool] = None,
        enabled_roles: Optional[List[Role]] = default_roles,
        callback_args: Dict[str, Dict] = {},
    ):
        super().__init__(
            callbacks=callbacks,
            default_on=default_on,
            logging_only=logging_only,
            guardrail_name=guardrail_name,
            enabled_roles=enabled_roles,
            callback_args=callback_args,
        )


# Define the TypedDicts
class LakeraCategoryThresholds(TypedDict, total=False):
    prompt_injection: float
    jailbreak: float


class MishikallmParams(TypedDict):
    guardrail: str
    mode: str
    api_key: Optional[str]
    api_base: Optional[str]

    # Lakera specific params
    category_thresholds: Optional[LakeraCategoryThresholds]

    # Bedrock specific params
    guardrailIdentifier: Optional[str]
    guardrailVersion: Optional[str]

    # Presidio params
    output_parse_pii: Optional[bool]
    presidio_ad_hoc_recognizers: Optional[str]
    mock_redacted_text: Optional[dict]

    # hide secrets params
    detect_secrets_config: Optional[dict]

    # guardrails ai params
    guard_name: Optional[str]
    default_on: Optional[bool]


class Guardrail(TypedDict, total=False):
    guardrail_name: str
    mishikallm_params: MishikallmParams
    guardrail_info: Optional[Dict]


class guardrailConfig(TypedDict):
    guardrails: List[Guardrail]


class GuardrailEventHooks(str, Enum):
    pre_call = "pre_call"
    post_call = "post_call"
    during_call = "during_call"
    logging_only = "logging_only"


class BedrockTextContent(TypedDict, total=False):
    text: str


class BedrockContentItem(TypedDict, total=False):
    text: BedrockTextContent


class BedrockRequest(TypedDict, total=False):
    source: Literal["INPUT", "OUTPUT"]
    content: List[BedrockContentItem]


class DynamicGuardrailParams(TypedDict):
    extra_body: Dict[str, Any]


class GuardrailMishikaLLMParamsResponse(BaseModel):
    """The returned MishikaLLM Params object for /guardrails/list"""

    guardrail: str
    mode: Union[str, List[str]]
    default_on: bool = Field(default=False)

    def __init__(self, **kwargs):
        default_on = kwargs.get("default_on")
        if default_on is None:
            default_on = False

        super().__init__(**kwargs)


class GuardrailInfoResponse(BaseModel):
    guardrail_name: str
    mishikallm_params: GuardrailMishikaLLMParamsResponse
    guardrail_info: Optional[Dict]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ListGuardrailsResponse(BaseModel):
    guardrails: List[GuardrailInfoResponse]
