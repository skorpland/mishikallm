import asyncio
from typing import TYPE_CHECKING, Any

from mishikallm.utils import calculate_max_parallel_requests

if TYPE_CHECKING:
    from mishikallm.router import Router as _Router

    MishikallmRouter = _Router
else:
    MishikallmRouter = Any


class InitalizeCachedClient:
    @staticmethod
    def set_max_parallel_requests_client(
        mishikallm_router_instance: MishikallmRouter, model: dict
    ):
        mishikallm_params = model.get("mishikallm_params", {})
        model_id = model["model_info"]["id"]
        rpm = mishikallm_params.get("rpm", None)
        tpm = mishikallm_params.get("tpm", None)
        max_parallel_requests = mishikallm_params.get("max_parallel_requests", None)
        calculated_max_parallel_requests = calculate_max_parallel_requests(
            rpm=rpm,
            max_parallel_requests=max_parallel_requests,
            tpm=tpm,
            default_max_parallel_requests=mishikallm_router_instance.default_max_parallel_requests,
        )
        if calculated_max_parallel_requests:
            semaphore = asyncio.Semaphore(calculated_max_parallel_requests)
            cache_key = f"{model_id}_max_parallel_requests_client"
            mishikallm_router_instance.cache.set_cache(
                key=cache_key,
                value=semaphore,
                local_only=True,
            )
