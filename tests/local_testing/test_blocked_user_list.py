# What is this?
## This tests the blocked user pre call hook for the proxy server


import asyncio
import os
import random
import sys
import time
import traceback
from datetime import datetime

from dotenv import load_dotenv
from fastapi import Request

load_dotenv()
import os

sys.path.insert(
    0, os.path.abspath("../..")
)  # Adds the parent directory to the system path
import asyncio
import logging

import pytest

import mishikallm
from mishikallm import Router, mock_completion
from mishikallm._logging import verbose_proxy_logger
from mishikallm.caching.caching import DualCache
from mishikallm.proxy._types import UserAPIKeyAuth
from mishikallm.proxy.enterprise.enterprise_hooks.blocked_user_list import (
    _ENTERPRISE_BlockedUserList,
)
from mishikallm.proxy.management_endpoints.internal_user_endpoints import (
    new_user,
    user_info,
    user_update,
)
from mishikallm.proxy.management_endpoints.key_management_endpoints import (
    delete_key_fn,
    generate_key_fn,
    generate_key_helper_fn,
    info_key_fn,
    update_key_fn,
)
from mishikallm.proxy.proxy_server import user_api_key_auth
from mishikallm.proxy.management_endpoints.customer_endpoints import block_user
from mishikallm.proxy.spend_tracking.spend_management_endpoints import (
    spend_key_fn,
    spend_user_fn,
    view_spend_logs,
)
from mishikallm.proxy.utils import PrismaClient, ProxyLogging, hash_token

verbose_proxy_logger.setLevel(level=logging.DEBUG)

from starlette.datastructures import URL

from mishikallm.caching.caching import DualCache
from mishikallm.proxy._types import (
    BlockUsers,
    DynamoDBArgs,
    GenerateKeyRequest,
    KeyRequest,
    NewUserRequest,
    UpdateKeyRequest,
)

proxy_logging_obj = ProxyLogging(user_api_key_cache=DualCache())


@pytest.fixture
def prisma_client():
    from mishikallm.proxy.proxy_cli import append_query_params

    ### add connection pool + pool timeout args
    params = {"connection_limit": 100, "pool_timeout": 60}
    database_url = os.getenv("DATABASE_URL")
    modified_url = append_query_params(database_url, params)
    os.environ["DATABASE_URL"] = modified_url

    # Assuming PrismaClient is a class that needs to be instantiated
    prisma_client = PrismaClient(
        database_url=os.environ["DATABASE_URL"], proxy_logging_obj=proxy_logging_obj
    )

    # Reset mishikallm.proxy.proxy_server.prisma_client to None
    mishikallm.proxy.proxy_server.mishikallm_proxy_budget_name = (
        f"mishikallm-proxy-budget-{time.time()}"
    )
    mishikallm.proxy.proxy_server.user_custom_key_generate = None

    return prisma_client


@pytest.mark.asyncio
async def test_block_user_check(prisma_client):
    """
    - Set a blocked user as a mishikallm module value
    - Test to see if a call with that user id is made, an error is raised
    - Test to see if a call without that user is passes
    """
    setattr(mishikallm.proxy.proxy_server, "prisma_client", prisma_client)
    setattr(mishikallm.proxy.proxy_server, "master_key", "sk-1234")

    mishikallm.blocked_user_list = ["user_id_1"]

    blocked_user_obj = _ENTERPRISE_BlockedUserList(
        prisma_client=mishikallm.proxy.proxy_server.prisma_client
    )

    _api_key = "sk-12345"
    _api_key = hash_token("sk-12345")
    user_api_key_dict = UserAPIKeyAuth(api_key=_api_key)
    local_cache = DualCache()

    ## Case 1: blocked user id passed
    try:
        await blocked_user_obj.async_pre_call_hook(
            user_api_key_dict=user_api_key_dict,
            cache=local_cache,
            call_type="completion",
            data={"user_id": "user_id_1"},
        )
        pytest.fail(f"Expected call to fail")
    except Exception as e:
        pass

    ## Case 2: normal user id passed
    try:
        await blocked_user_obj.async_pre_call_hook(
            user_api_key_dict=user_api_key_dict,
            cache=local_cache,
            call_type="completion",
            data={"user_id": "user_id_2"},
        )
    except Exception as e:
        pytest.fail(f"An error occurred - {str(e)}")


@pytest.mark.asyncio
async def test_block_user_db_check(prisma_client):
    """
    - Block end user via "/user/block"
    - Check returned value
    """
    setattr(mishikallm.proxy.proxy_server, "prisma_client", prisma_client)
    setattr(mishikallm.proxy.proxy_server, "master_key", "sk-1234")
    await mishikallm.proxy.proxy_server.prisma_client.connect()
    _block_users = BlockUsers(user_ids=["user_id_1"])
    result = await block_user(data=_block_users)
    result = result["blocked_users"]
    assert len(result) == 1
    assert result[0].user_id == "user_id_1"
    assert result[0].blocked == True
