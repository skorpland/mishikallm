"""
Helper functions to get/set num success and num failures per deployment 


set_deployment_failures_for_current_minute
set_deployment_successes_for_current_minute

get_deployment_failures_for_current_minute
get_deployment_successes_for_current_minute
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mishikallm.router import Router as _Router

    MishikallmRouter = _Router
else:
    MishikallmRouter = Any


def increment_deployment_successes_for_current_minute(
    mishikallm_router_instance: MishikallmRouter,
    deployment_id: str,
) -> str:
    """
    In-Memory: Increments the number of successes for the current minute for a deployment_id
    """
    key = f"{deployment_id}:successes"
    mishikallm_router_instance.cache.increment_cache(
        local_only=True,
        key=key,
        value=1,
        ttl=60,
    )
    return key


def increment_deployment_failures_for_current_minute(
    mishikallm_router_instance: MishikallmRouter,
    deployment_id: str,
):
    """
    In-Memory: Increments the number of failures for the current minute for a deployment_id
    """
    key = f"{deployment_id}:fails"
    mishikallm_router_instance.cache.increment_cache(
        local_only=True,
        key=key,
        value=1,
        ttl=60,
    )


def get_deployment_successes_for_current_minute(
    mishikallm_router_instance: MishikallmRouter,
    deployment_id: str,
) -> int:
    """
    Returns the number of successes for the current minute for a deployment_id

    Returns 0 if no value found
    """
    key = f"{deployment_id}:successes"
    return (
        mishikallm_router_instance.cache.get_cache(
            local_only=True,
            key=key,
        )
        or 0
    )


def get_deployment_failures_for_current_minute(
    mishikallm_router_instance: MishikallmRouter,
    deployment_id: str,
) -> int:
    """
    Returns the number of fails for the current minute for a deployment_id

    Returns 0 if no value found
    """
    key = f"{deployment_id}:fails"
    return (
        mishikallm_router_instance.cache.get_cache(
            local_only=True,
            key=key,
        )
        or 0
    )
