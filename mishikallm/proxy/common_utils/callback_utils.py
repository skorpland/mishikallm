from typing import Any, Dict, List, Optional

import mishikallm
from mishikallm import get_secret
from mishikallm._logging import verbose_proxy_logger
from mishikallm.proxy._types import CommonProxyErrors, MishikaLLMPromptInjectionParams
from mishikallm.proxy.types_utils.utils import get_instance_fn

blue_color_code = "\033[94m"
reset_color_code = "\033[0m"


def initialize_callbacks_on_proxy(  # noqa: PLR0915
    value: Any,
    premium_user: bool,
    config_file_path: str,
    mishikallm_settings: dict,
    callback_specific_params: dict = {},
):
    from mishikallm.proxy.proxy_server import prisma_client

    verbose_proxy_logger.debug(
        f"{blue_color_code}initializing callbacks={value} on proxy{reset_color_code}"
    )
    if isinstance(value, list):
        imported_list: List[Any] = []
        for callback in value:  # ["presidio", <my-custom-callback>]
            if (
                isinstance(callback, str)
                and callback in mishikallm._known_custom_logger_compatible_callbacks
            ):
                imported_list.append(callback)
            elif isinstance(callback, str) and callback == "presidio":
                from mishikallm.proxy.guardrails.guardrail_hooks.presidio import (
                    _OPTIONAL_PresidioPIIMasking,
                )

                presidio_logging_only: Optional[bool] = mishikallm_settings.get(
                    "presidio_logging_only", None
                )
                if presidio_logging_only is not None:
                    presidio_logging_only = bool(
                        presidio_logging_only
                    )  # validate boolean given

                _presidio_params = {}
                if "presidio" in callback_specific_params and isinstance(
                    callback_specific_params["presidio"], dict
                ):
                    _presidio_params = callback_specific_params["presidio"]

                params: Dict[str, Any] = {
                    "logging_only": presidio_logging_only,
                    **_presidio_params,
                }
                pii_masking_object = _OPTIONAL_PresidioPIIMasking(**params)
                imported_list.append(pii_masking_object)
            elif isinstance(callback, str) and callback == "llamaguard_moderations":
                from enterprise.enterprise_hooks.llama_guard import (
                    _ENTERPRISE_LlamaGuard,
                )

                if premium_user is not True:
                    raise Exception(
                        "Trying to use Llama Guard"
                        + CommonProxyErrors.not_premium_user.value
                    )

                llama_guard_object = _ENTERPRISE_LlamaGuard()
                imported_list.append(llama_guard_object)
            elif isinstance(callback, str) and callback == "hide_secrets":
                from enterprise.enterprise_hooks.secret_detection import (
                    _ENTERPRISE_SecretDetection,
                )

                if premium_user is not True:
                    raise Exception(
                        "Trying to use secret hiding"
                        + CommonProxyErrors.not_premium_user.value
                    )

                _secret_detection_object = _ENTERPRISE_SecretDetection()
                imported_list.append(_secret_detection_object)
            elif isinstance(callback, str) and callback == "openai_moderations":
                from enterprise.enterprise_hooks.openai_moderation import (
                    _ENTERPRISE_OpenAI_Moderation,
                )

                if premium_user is not True:
                    raise Exception(
                        "Trying to use OpenAI Moderations Check"
                        + CommonProxyErrors.not_premium_user.value
                    )

                openai_moderations_object = _ENTERPRISE_OpenAI_Moderation()
                imported_list.append(openai_moderations_object)
            elif isinstance(callback, str) and callback == "lakera_prompt_injection":
                from mishikallm.proxy.guardrails.guardrail_hooks.lakera_ai import (
                    lakeraAI_Moderation,
                )

                init_params = {}
                if "lakera_prompt_injection" in callback_specific_params:
                    init_params = callback_specific_params["lakera_prompt_injection"]
                lakera_moderations_object = lakeraAI_Moderation(**init_params)
                imported_list.append(lakera_moderations_object)
            elif isinstance(callback, str) and callback == "aporia_prompt_injection":
                from mishikallm.proxy.guardrails.guardrail_hooks.aporia_ai import (
                    AporiaGuardrail,
                )

                aporia_guardrail_object = AporiaGuardrail()
                imported_list.append(aporia_guardrail_object)
            elif isinstance(callback, str) and callback == "google_text_moderation":
                from enterprise.enterprise_hooks.google_text_moderation import (
                    _ENTERPRISE_GoogleTextModeration,
                )

                if premium_user is not True:
                    raise Exception(
                        "Trying to use Google Text Moderation"
                        + CommonProxyErrors.not_premium_user.value
                    )

                google_text_moderation_obj = _ENTERPRISE_GoogleTextModeration()
                imported_list.append(google_text_moderation_obj)
            elif isinstance(callback, str) and callback == "llmguard_moderations":
                from enterprise.enterprise_hooks.llm_guard import _ENTERPRISE_LLMGuard

                if premium_user is not True:
                    raise Exception(
                        "Trying to use Llm Guard"
                        + CommonProxyErrors.not_premium_user.value
                    )

                llm_guard_moderation_obj = _ENTERPRISE_LLMGuard()
                imported_list.append(llm_guard_moderation_obj)
            elif isinstance(callback, str) and callback == "blocked_user_check":
                from enterprise.enterprise_hooks.blocked_user_list import (
                    _ENTERPRISE_BlockedUserList,
                )

                if premium_user is not True:
                    raise Exception(
                        "Trying to use ENTERPRISE BlockedUser"
                        + CommonProxyErrors.not_premium_user.value
                    )

                blocked_user_list = _ENTERPRISE_BlockedUserList(
                    prisma_client=prisma_client
                )
                imported_list.append(blocked_user_list)
            elif isinstance(callback, str) and callback == "banned_keywords":
                from enterprise.enterprise_hooks.banned_keywords import (
                    _ENTERPRISE_BannedKeywords,
                )

                if premium_user is not True:
                    raise Exception(
                        "Trying to use ENTERPRISE BannedKeyword"
                        + CommonProxyErrors.not_premium_user.value
                    )

                banned_keywords_obj = _ENTERPRISE_BannedKeywords()
                imported_list.append(banned_keywords_obj)
            elif isinstance(callback, str) and callback == "detect_prompt_injection":
                from mishikallm.proxy.hooks.prompt_injection_detection import (
                    _OPTIONAL_PromptInjectionDetection,
                )

                prompt_injection_params = None
                if "prompt_injection_params" in mishikallm_settings:
                    prompt_injection_params_in_config = mishikallm_settings[
                        "prompt_injection_params"
                    ]
                    prompt_injection_params = MishikaLLMPromptInjectionParams(
                        **prompt_injection_params_in_config
                    )

                prompt_injection_detection_obj = _OPTIONAL_PromptInjectionDetection(
                    prompt_injection_params=prompt_injection_params,
                )
                imported_list.append(prompt_injection_detection_obj)
            elif isinstance(callback, str) and callback == "batch_redis_requests":
                from mishikallm.proxy.hooks.batch_redis_get import (
                    _PROXY_BatchRedisRequests,
                )

                batch_redis_obj = _PROXY_BatchRedisRequests()
                imported_list.append(batch_redis_obj)
            elif isinstance(callback, str) and callback == "azure_content_safety":
                from mishikallm.proxy.hooks.azure_content_safety import (
                    _PROXY_AzureContentSafety,
                )

                azure_content_safety_params = mishikallm_settings[
                    "azure_content_safety_params"
                ]
                for k, v in azure_content_safety_params.items():
                    if (
                        v is not None
                        and isinstance(v, str)
                        and v.startswith("os.environ/")
                    ):
                        azure_content_safety_params[k] = get_secret(v)

                azure_content_safety_obj = _PROXY_AzureContentSafety(
                    **azure_content_safety_params,
                )
                imported_list.append(azure_content_safety_obj)
            else:
                verbose_proxy_logger.debug(
                    f"{blue_color_code} attempting to import custom calback={callback} {reset_color_code}"
                )
                imported_list.append(
                    get_instance_fn(
                        value=callback,
                        config_file_path=config_file_path,
                    )
                )
        if isinstance(mishikallm.callbacks, list):
            mishikallm.callbacks.extend(imported_list)
        else:
            mishikallm.callbacks = imported_list  # type: ignore

        if "prometheus" in value:
            from mishikallm.integrations.prometheus import PrometheusLogger

            PrometheusLogger._mount_metrics_endpoint(premium_user)
    else:
        mishikallm.callbacks = [
            get_instance_fn(
                value=value,
                config_file_path=config_file_path,
            )
        ]
    verbose_proxy_logger.debug(
        f"{blue_color_code} Initialized Callbacks - {mishikallm.callbacks} {reset_color_code}"
    )


def get_model_group_from_mishikallm_kwargs(kwargs: dict) -> Optional[str]:
    _mishikallm_params = kwargs.get("mishikallm_params", None) or {}
    _metadata = _mishikallm_params.get("metadata", None) or {}
    _model_group = _metadata.get("model_group", None)
    if _model_group is not None:
        return _model_group

    return None


def get_model_group_from_request_data(data: dict) -> Optional[str]:
    _metadata = data.get("metadata", None) or {}
    _model_group = _metadata.get("model_group", None)
    if _model_group is not None:
        return _model_group

    return None


def get_remaining_tokens_and_requests_from_request_data(data: Dict) -> Dict[str, str]:
    """
    Helper function to return x-mishikallm-key-remaining-tokens-{model_group} and x-mishikallm-key-remaining-requests-{model_group}

    Returns {} when api_key + model rpm/tpm limit is not set

    """
    headers = {}
    _metadata = data.get("metadata", None) or {}
    model_group = get_model_group_from_request_data(data)

    # Remaining Requests
    remaining_requests_variable_name = f"mishikallm-key-remaining-requests-{model_group}"
    remaining_requests = _metadata.get(remaining_requests_variable_name, None)
    if remaining_requests:
        headers[f"x-mishikallm-key-remaining-requests-{model_group}"] = remaining_requests

    # Remaining Tokens
    remaining_tokens_variable_name = f"mishikallm-key-remaining-tokens-{model_group}"
    remaining_tokens = _metadata.get(remaining_tokens_variable_name, None)
    if remaining_tokens:
        headers[f"x-mishikallm-key-remaining-tokens-{model_group}"] = remaining_tokens

    return headers


def get_logging_caching_headers(request_data: Dict) -> Optional[Dict]:
    _metadata = request_data.get("metadata", None) or {}
    headers = {}
    if "applied_guardrails" in _metadata:
        headers["x-mishikallm-applied-guardrails"] = ",".join(
            _metadata["applied_guardrails"]
        )

    if "semantic-similarity" in _metadata:
        headers["x-mishikallm-semantic-similarity"] = str(_metadata["semantic-similarity"])

    return headers


def add_guardrail_to_applied_guardrails_header(
    request_data: Dict, guardrail_name: Optional[str]
):
    if guardrail_name is None:
        return
    _metadata = request_data.get("metadata", None) or {}
    if "applied_guardrails" in _metadata:
        _metadata["applied_guardrails"].append(guardrail_name)
    else:
        _metadata["applied_guardrails"] = [guardrail_name]
