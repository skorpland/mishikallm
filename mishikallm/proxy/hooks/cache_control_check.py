# What this does?
## Checks if key is allowed to use the cache controls passed in to the completion() call


from fastapi import HTTPException

from mishikallm import verbose_logger
from mishikallm._logging import verbose_proxy_logger
from mishikallm.caching.caching import DualCache
from mishikallm.integrations.custom_logger import CustomLogger
from mishikallm.proxy._types import UserAPIKeyAuth


class _PROXY_CacheControlCheck(CustomLogger):
    # Class variables or attributes
    def __init__(self):
        pass

    async def async_pre_call_hook(
        self,
        user_api_key_dict: UserAPIKeyAuth,
        cache: DualCache,
        data: dict,
        call_type: str,
    ):
        try:
            verbose_proxy_logger.debug("Inside Cache Control Check Pre-Call Hook")
            allowed_cache_controls = user_api_key_dict.allowed_cache_controls

            if data.get("cache", None) is None:
                return

            cache_args = data.get("cache", None)
            if isinstance(cache_args, dict):
                for k, v in cache_args.items():
                    if (
                        (allowed_cache_controls is not None)
                        and (isinstance(allowed_cache_controls, list))
                        and (
                            len(allowed_cache_controls) > 0
                        )  # assume empty list to be nullable - https://github.com/prisma/prisma/issues/847#issuecomment-546895663
                        and k not in allowed_cache_controls
                    ):
                        raise HTTPException(
                            status_code=403,
                            detail=f"Not allowed to set {k} as a cache control. Contact admin to change permissions.",
                        )
            else:  # invalid cache
                return

        except HTTPException as e:
            raise e
        except Exception as e:
            verbose_logger.exception(
                "mishikallm.proxy.hooks.cache_control_check.py::async_pre_call_hook(): Exception occured - {}".format(
                    str(e)
                )
            )
