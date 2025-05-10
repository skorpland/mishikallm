# mishikallm/proxy/guardrails/guardrail_initializers.py
import mishikallm
from mishikallm.types.guardrails import *


def initialize_aporia(mishikallm_params, guardrail):
    from mishikallm.proxy.guardrails.guardrail_hooks.aporia_ai import AporiaGuardrail

    _aporia_callback = AporiaGuardrail(
        api_base=mishikallm_params["api_base"],
        api_key=mishikallm_params["api_key"],
        guardrail_name=guardrail["guardrail_name"],
        event_hook=mishikallm_params["mode"],
        default_on=mishikallm_params["default_on"],
    )
    mishikallm.logging_callback_manager.add_mishikallm_callback(_aporia_callback)


def initialize_bedrock(mishikallm_params, guardrail):
    from mishikallm.proxy.guardrails.guardrail_hooks.bedrock_guardrails import (
        BedrockGuardrail,
    )

    _bedrock_callback = BedrockGuardrail(
        guardrail_name=guardrail["guardrail_name"],
        event_hook=mishikallm_params["mode"],
        guardrailIdentifier=mishikallm_params["guardrailIdentifier"],
        guardrailVersion=mishikallm_params["guardrailVersion"],
        default_on=mishikallm_params["default_on"],
    )
    mishikallm.logging_callback_manager.add_mishikallm_callback(_bedrock_callback)


def initialize_lakera(mishikallm_params, guardrail):
    from mishikallm.proxy.guardrails.guardrail_hooks.lakera_ai import lakeraAI_Moderation

    _lakera_callback = lakeraAI_Moderation(
        api_base=mishikallm_params["api_base"],
        api_key=mishikallm_params["api_key"],
        guardrail_name=guardrail["guardrail_name"],
        event_hook=mishikallm_params["mode"],
        category_thresholds=mishikallm_params.get("category_thresholds"),
        default_on=mishikallm_params["default_on"],
    )
    mishikallm.logging_callback_manager.add_mishikallm_callback(_lakera_callback)


def initialize_aim(mishikallm_params, guardrail):
    from mishikallm.proxy.guardrails.guardrail_hooks.aim import AimGuardrail

    _aim_callback = AimGuardrail(
        api_base=mishikallm_params["api_base"],
        api_key=mishikallm_params["api_key"],
        guardrail_name=guardrail["guardrail_name"],
        event_hook=mishikallm_params["mode"],
        default_on=mishikallm_params["default_on"],
    )
    mishikallm.logging_callback_manager.add_mishikallm_callback(_aim_callback)


def initialize_presidio(mishikallm_params, guardrail):
    from mishikallm.proxy.guardrails.guardrail_hooks.presidio import (
        _OPTIONAL_PresidioPIIMasking,
    )

    _presidio_callback = _OPTIONAL_PresidioPIIMasking(
        guardrail_name=guardrail["guardrail_name"],
        event_hook=mishikallm_params["mode"],
        output_parse_pii=mishikallm_params["output_parse_pii"],
        presidio_ad_hoc_recognizers=mishikallm_params["presidio_ad_hoc_recognizers"],
        mock_redacted_text=mishikallm_params.get("mock_redacted_text") or None,
        default_on=mishikallm_params["default_on"],
    )
    mishikallm.logging_callback_manager.add_mishikallm_callback(_presidio_callback)

    if mishikallm_params["output_parse_pii"]:
        _success_callback = _OPTIONAL_PresidioPIIMasking(
            output_parse_pii=True,
            guardrail_name=guardrail["guardrail_name"],
            event_hook=GuardrailEventHooks.post_call.value,
            presidio_ad_hoc_recognizers=mishikallm_params["presidio_ad_hoc_recognizers"],
            default_on=mishikallm_params["default_on"],
        )
        mishikallm.logging_callback_manager.add_mishikallm_callback(_success_callback)


def initialize_hide_secrets(mishikallm_params, guardrail):
    from enterprise.enterprise_hooks.secret_detection import _ENTERPRISE_SecretDetection

    _secret_detection_object = _ENTERPRISE_SecretDetection(
        detect_secrets_config=mishikallm_params.get("detect_secrets_config"),
        event_hook=mishikallm_params["mode"],
        guardrail_name=guardrail["guardrail_name"],
        default_on=mishikallm_params["default_on"],
    )
    mishikallm.logging_callback_manager.add_mishikallm_callback(_secret_detection_object)


def initialize_guardrails_ai(mishikallm_params, guardrail):
    from mishikallm.proxy.guardrails.guardrail_hooks.guardrails_ai import GuardrailsAI

    _guard_name = mishikallm_params.get("guard_name")
    if not _guard_name:
        raise Exception(
            "GuardrailsAIException - Please pass the Guardrails AI guard name via 'mishikallm_params::guard_name'"
        )

    _guardrails_ai_callback = GuardrailsAI(
        api_base=mishikallm_params.get("api_base"),
        guard_name=_guard_name,
        guardrail_name=SupportedGuardrailIntegrations.GURDRAILS_AI.value,
        default_on=mishikallm_params["default_on"],
    )
    mishikallm.logging_callback_manager.add_mishikallm_callback(_guardrails_ai_callback)
