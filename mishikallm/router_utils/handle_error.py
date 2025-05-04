from typing import TYPE_CHECKING, Any, Optional, Union

from mishikallm._logging import verbose_router_logger
from mishikallm.constants import MAX_EXCEPTION_MESSAGE_LENGTH
from mishikallm.router_utils.cooldown_handlers import (
    _async_get_cooldown_deployments_with_debug_info,
)
from mishikallm.types.integrations.slack_alerting import AlertType
from mishikallm.types.router import RouterRateLimitError

if TYPE_CHECKING:
    from opentelemetry.trace import Span as _Span

    from mishikallm.router import Router as _Router

    MishikallmRouter = _Router
    Span = Union[_Span, Any]
else:
    MishikallmRouter = Any
    Span = Any


async def send_llm_exception_alert(
    mishikallm_router_instance: MishikallmRouter,
    request_kwargs: dict,
    error_traceback_str: str,
    original_exception,
):
    """
    Only runs if router.slack_alerting_logger is set
    Sends a Slack / MS Teams alert for the LLM API call failure. Only if router.slack_alerting_logger is set.

    Parameters:
        mishikallm_router_instance (_Router): The MishikallmRouter instance.
        original_exception (Any): The original exception that occurred.

    Returns:
        None
    """
    if mishikallm_router_instance is None:
        return

    if not hasattr(mishikallm_router_instance, "slack_alerting_logger"):
        return

    if mishikallm_router_instance.slack_alerting_logger is None:
        return

    if "proxy_server_request" in request_kwargs:
        # Do not send any alert if it's a request from mishikallm proxy server request
        # the proxy is already instrumented to send LLM API call failures
        return

    mishikallm_debug_info = getattr(original_exception, "mishikallm_debug_info", None)
    exception_str = str(original_exception)
    if mishikallm_debug_info is not None:
        exception_str += mishikallm_debug_info
    exception_str += f"\n\n{error_traceback_str[:MAX_EXCEPTION_MESSAGE_LENGTH]}"

    await mishikallm_router_instance.slack_alerting_logger.send_alert(
        message=f"LLM API call failed: `{exception_str}`",
        level="High",
        alert_type=AlertType.llm_exceptions,
        alerting_metadata={},
    )


async def async_raise_no_deployment_exception(
    mishikallm_router_instance: MishikallmRouter, model: str, parent_otel_span: Optional[Span]
):
    """
    Raises a RouterRateLimitError if no deployment is found for the given model.
    """
    verbose_router_logger.info(
        f"get_available_deployment for model: {model}, No deployment available"
    )
    model_ids = mishikallm_router_instance.get_model_ids(model_name=model)
    _cooldown_time = mishikallm_router_instance.cooldown_cache.get_min_cooldown(
        model_ids=model_ids, parent_otel_span=parent_otel_span
    )
    _cooldown_list = await _async_get_cooldown_deployments_with_debug_info(
        mishikallm_router_instance=mishikallm_router_instance,
        parent_otel_span=parent_otel_span,
    )
    return RouterRateLimitError(
        model=model,
        cooldown_time=_cooldown_time,
        enable_pre_call_checks=mishikallm_router_instance.enable_pre_call_checks,
        cooldown_list=_cooldown_list,
    )
