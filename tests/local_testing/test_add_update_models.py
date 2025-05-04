import sys, os
import traceback
import json
import uuid
from dotenv import load_dotenv
from fastapi import Request
from datetime import datetime

load_dotenv()
import os, io, time

# this file is to test mishikallm/proxy

sys.path.insert(
    0, os.path.abspath("../..")
)  # Adds the parent directory to the system path
import pytest, logging, asyncio
import mishikallm
from mishikallm.proxy.management_endpoints.model_management_endpoints import (
    add_new_model,
    update_model,
)
from mishikallm.proxy._types import MishikallmUserRoles
from mishikallm._logging import verbose_proxy_logger
from mishikallm.proxy.utils import PrismaClient, ProxyLogging
from mishikallm.proxy.management_endpoints.team_endpoints import new_team

verbose_proxy_logger.setLevel(level=logging.DEBUG)
from mishikallm.caching.caching import DualCache
from mishikallm.router import (
    Deployment,
    MishikaLLM_Params,
)
from mishikallm.types.router import ModelInfo, updateDeployment, updateMishikaLLMParams

from mishikallm.proxy._types import UserAPIKeyAuth, NewTeamRequest, MishikaLLM_TeamTable

proxy_logging_obj = ProxyLogging(user_api_key_cache=DualCache())


@pytest.fixture
def prisma_client():
    from mishikallm.proxy.proxy_cli import append_query_params

    ### add connection pool + pool timeout args
    params = {"connection_limit": 100, "pool_timeout": 60}
    database_url = os.getenv("DATABASE_URL")
    modified_url = append_query_params(database_url, params)
    os.environ["DATABASE_URL"] = modified_url
    os.environ["STORE_MODEL_IN_DB"] = "true"

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
@pytest.mark.skip(reason="new feature, tests passing locally")
async def test_add_new_model(prisma_client):
    setattr(mishikallm.proxy.proxy_server, "prisma_client", prisma_client)
    setattr(mishikallm.proxy.proxy_server, "master_key", "sk-1234")
    setattr(mishikallm.proxy.proxy_server, "store_model_in_db", True)

    await mishikallm.proxy.proxy_server.prisma_client.connect()
    from mishikallm.proxy.proxy_server import user_api_key_cache
    import uuid

    _new_model_id = f"local-test-{uuid.uuid4().hex}"

    await add_new_model(
        model_params=Deployment(
            model_name="test_model",
            mishikallm_params=MishikaLLM_Params(
                model="azure/gpt-3.5-turbo",
                api_key="test_api_key",
                api_base="test_api_base",
                rpm=1000,
                tpm=1000,
            ),
            model_info=ModelInfo(
                id=_new_model_id,
            ),
        ),
        user_api_key_dict=UserAPIKeyAuth(
            user_role=MishikallmUserRoles.PROXY_ADMIN.value,
            api_key="sk-1234",
            user_id="1234",
        ),
    )

    _new_models = await prisma_client.db.mishikallm_proxymodeltable.find_many()
    print("_new_models: ", _new_models)

    _new_model_in_db = None
    for model in _new_models:
        print("current model: ", model)
        if model.model_info["id"] == _new_model_id:
            print("FOUND MODEL: ", model)
            _new_model_in_db = model

    assert _new_model_in_db is not None


@pytest.mark.asyncio
@pytest.mark.skip(reason="new feature, tests passing locally")
async def test_add_update_model(prisma_client):
    # test that existing mishikallm_params are not updated
    # only new / updated params get updated
    setattr(mishikallm.proxy.proxy_server, "prisma_client", prisma_client)
    setattr(mishikallm.proxy.proxy_server, "master_key", "sk-1234")
    setattr(mishikallm.proxy.proxy_server, "store_model_in_db", True)

    await mishikallm.proxy.proxy_server.prisma_client.connect()
    from mishikallm.proxy.proxy_server import user_api_key_cache
    import uuid

    _new_model_id = f"local-test-{uuid.uuid4().hex}"

    await add_new_model(
        model_params=Deployment(
            model_name="test_model",
            mishikallm_params=MishikaLLM_Params(
                model="azure/gpt-3.5-turbo",
                api_key="test_api_key",
                api_base="test_api_base",
                rpm=1000,
                tpm=1000,
            ),
            model_info=ModelInfo(
                id=_new_model_id,
            ),
        ),
        user_api_key_dict=UserAPIKeyAuth(
            user_role=MishikallmUserRoles.PROXY_ADMIN.value,
            api_key="sk-1234",
            user_id="1234",
        ),
    )

    _new_models = await prisma_client.db.mishikallm_proxymodeltable.find_many()
    print("_new_models: ", _new_models)

    _new_model_in_db = None
    for model in _new_models:
        print("current model: ", model)
        if model.model_info["id"] == _new_model_id:
            print("FOUND MODEL: ", model)
            _new_model_in_db = model

    assert _new_model_in_db is not None

    _original_model = _new_model_in_db
    _original_mishikallm_params = _new_model_in_db.mishikallm_params
    print("_original_mishikallm_params: ", _original_mishikallm_params)
    print("now updating the tpm for model")
    # run update to update "tpm"
    await update_model(
        model_params=updateDeployment(
            mishikallm_params=updateMishikaLLMParams(tpm=123456),
            model_info=ModelInfo(
                id=_new_model_id,
            ),
        ),
        user_api_key_dict=UserAPIKeyAuth(
            user_role=MishikallmUserRoles.PROXY_ADMIN.value,
            api_key="sk-1234",
            user_id="1234",
        ),
    )

    _new_models = await prisma_client.db.mishikallm_proxymodeltable.find_many()

    _new_model_in_db = None
    for model in _new_models:
        if model.model_info["id"] == _new_model_id:
            print("\nFOUND MODEL: ", model)
            _new_model_in_db = model

    # assert all other mishikallm params are identical to _original_mishikallm_params
    for key, value in _original_mishikallm_params.items():
        if key == "tpm":
            # assert that tpm actually got updated
            assert _new_model_in_db.mishikallm_params[key] == 123456
        else:
            assert _new_model_in_db.mishikallm_params[key] == value

    assert _original_model.model_id == _new_model_in_db.model_id
    assert _original_model.model_name == _new_model_in_db.model_name
    assert _original_model.model_info == _new_model_in_db.model_info


async def _create_new_team(prisma_client):
    new_team_request = NewTeamRequest(
        team_alias=f"team_{uuid.uuid4().hex}",
    )
    _new_team = await new_team(
        data=new_team_request,
        user_api_key_dict=UserAPIKeyAuth(
            user_role=MishikallmUserRoles.PROXY_ADMIN.value,
            api_key="sk-1234",
            user_id="1234",
        ),
        http_request=Request(
            scope={"type": "http", "method": "POST", "path": "/new_team"}
        ),
    )
    return MishikaLLM_TeamTable(**_new_team)


@pytest.mark.asyncio
async def test_add_team_model_to_db(prisma_client):
    """
    Test adding a team model and verifying the team_public_model_name is stored correctly
    """
    setattr(mishikallm.proxy.proxy_server, "prisma_client", prisma_client)
    setattr(mishikallm.proxy.proxy_server, "master_key", "sk-1234")
    setattr(mishikallm.proxy.proxy_server, "store_model_in_db", True)

    await mishikallm.proxy.proxy_server.prisma_client.connect()

    from mishikallm.proxy.management_endpoints.model_management_endpoints import (
        _add_team_model_to_db,
    )
    import uuid

    new_team = await _create_new_team(prisma_client)
    team_id = new_team.team_id

    public_model_name = "my-gpt4-model"
    model_id = f"local-test-{uuid.uuid4().hex}"

    # Create test model deployment
    model_params = Deployment(
        model_name=public_model_name,
        mishikallm_params=MishikaLLM_Params(
            model="gpt-4",
            api_key="test_api_key",
        ),
        model_info=ModelInfo(
            id=model_id,
            team_id=team_id,
        ),
    )

    # Add model to db
    model_response = await _add_team_model_to_db(
        model_params=model_params,
        user_api_key_dict=UserAPIKeyAuth(
            user_role=MishikallmUserRoles.PROXY_ADMIN.value,
            api_key="sk-1234",
            user_id="1234",
            team_id=team_id,
        ),
        prisma_client=prisma_client,
    )

    # Verify model was created with correct attributes
    assert model_response is not None
    assert model_response.model_name.startswith(f"model_name_{team_id}")

    # Verify team_public_model_name was stored in model_info
    model_info = model_response.model_info
    assert model_info["team_public_model_name"] == public_model_name

    await asyncio.sleep(1)

    # Verify team model alias was created
    team = await prisma_client.db.mishikallm_teamtable.find_first(
        where={
            "team_id": team_id,
        },
        include={"mishikallm_model_table": True},
    )
    print("team=", team.model_dump_json())
    assert team is not None

    team_model = team.model_id
    print("team model id=", team_model)
    mishikallm_model_table = team.mishikallm_model_table
    print("mishikallm_model_table=", mishikallm_model_table.model_dump_json())
    model_aliases = mishikallm_model_table.model_aliases
    print("model_aliases=", model_aliases)

    assert public_model_name in model_aliases
    assert model_aliases[public_model_name] == model_response.model_name
