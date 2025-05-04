import os
import sys
import traceback
import uuid
from datetime import datetime

from dotenv import load_dotenv
from fastapi import Request
from fastapi.routing import APIRoute


import io
import os
import time

# this file is to test mishikallm/proxy

sys.path.insert(
    0, os.path.abspath("../..")
)  # Adds the parent directory to the system path
import asyncio
import logging

load_dotenv()

import pytest
import uuid
import mishikallm
from mishikallm._logging import verbose_proxy_logger

from mishikallm.proxy.proxy_server import (
    MishikallmUserRoles,
    audio_transcriptions,
    chat_completion,
    completion,
    embeddings,
    image_generation,
    model_list,
    moderations,
    user_api_key_auth,
)

from mishikallm.proxy.utils import PrismaClient, ProxyLogging, hash_token, update_spend

verbose_proxy_logger.setLevel(level=logging.DEBUG)

from starlette.datastructures import URL

from mishikallm.proxy.management_helpers.audit_logs import create_audit_log_for_update
from mishikallm.proxy._types import MishikaLLM_AuditLogs, MishikallmTableNames
from mishikallm.caching.caching import DualCache
from unittest.mock import patch, AsyncMock

proxy_logging_obj = ProxyLogging(user_api_key_cache=DualCache())
import json


@pytest.mark.asyncio
async def test_create_audit_log_for_update_premium_user():
    """
    Basic unit test for create_audit_log_for_update

    Test that the audit log is created when a premium user updates a team
    """
    with patch("mishikallm.proxy.proxy_server.premium_user", True), patch(
        "mishikallm.store_audit_logs", True
    ), patch("mishikallm.proxy.proxy_server.prisma_client") as mock_prisma:

        mock_prisma.db.mishikallm_auditlog.create = AsyncMock()

        request_data = MishikaLLM_AuditLogs(
            id="test_id",
            updated_at=datetime.now(),
            changed_by="test_changed_by",
            action="updated",
            table_name=MishikallmTableNames.TEAM_TABLE_NAME,
            object_id="test_object_id",
            updated_values=json.dumps({"key": "value"}),
            before_value=json.dumps({"old_key": "old_value"}),
        )

        await create_audit_log_for_update(request_data)

        mock_prisma.db.mishikallm_auditlog.create.assert_called_once_with(
            data={
                "id": "test_id",
                "updated_at": request_data.updated_at,
                "changed_by": request_data.changed_by,
                "action": request_data.action,
                "table_name": request_data.table_name,
                "object_id": request_data.object_id,
                "updated_values": request_data.updated_values,
                "before_value": request_data.before_value,
            }
        )


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

    return prisma_client


@pytest.mark.asyncio()
async def test_create_audit_log_in_db(prisma_client):
    print("prisma client=", prisma_client)

    setattr(mishikallm.proxy.proxy_server, "prisma_client", prisma_client)
    setattr(mishikallm.proxy.proxy_server, "master_key", "sk-1234")
    setattr(mishikallm.proxy.proxy_server, "premium_user", True)
    setattr(mishikallm, "store_audit_logs", True)

    await mishikallm.proxy.proxy_server.prisma_client.connect()
    audit_log_id = f"audit_log_id_{uuid.uuid4()}"

    # create a audit log for /key/generate
    request_data = MishikaLLM_AuditLogs(
        id=audit_log_id,
        updated_at=datetime.now(),
        changed_by="test_changed_by",
        action="updated",
        table_name=MishikallmTableNames.TEAM_TABLE_NAME,
        object_id="test_object_id",
        updated_values=json.dumps({"key": "value"}),
        before_value=json.dumps({"old_key": "old_value"}),
    )

    await create_audit_log_for_update(request_data)

    await asyncio.sleep(1)

    # now read the last log from the db
    last_log = await prisma_client.db.mishikallm_auditlog.find_first(
        where={"id": audit_log_id}
    )

    assert last_log.id == audit_log_id

    setattr(mishikallm, "store_audit_logs", False)
