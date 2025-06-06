from typing import Any, Union

from mishikallm.proxy._types import (
    GenerateKeyRequest,
    MishikaLLM_ManagementEndpoint_MetadataFields_Premium,
    MishikaLLM_TeamTable,
    MishikallmUserRoles,
    UserAPIKeyAuth,
)
from mishikallm.proxy.utils import _premium_user_check


def _user_has_admin_view(user_api_key_dict: UserAPIKeyAuth) -> bool:
    return (
        user_api_key_dict.user_role == MishikallmUserRoles.PROXY_ADMIN
        or user_api_key_dict.user_role == MishikallmUserRoles.PROXY_ADMIN_VIEW_ONLY
    )


def _is_user_team_admin(
    user_api_key_dict: UserAPIKeyAuth, team_obj: MishikaLLM_TeamTable
) -> bool:
    for member in team_obj.members_with_roles:
        if (
            member.user_id is not None and member.user_id == user_api_key_dict.user_id
        ) and member.role == "admin":
            return True

    return False


def _set_object_metadata_field(
    object_data: Union[MishikaLLM_TeamTable, GenerateKeyRequest],
    field_name: str,
    value: Any,
) -> None:
    """
    Helper function to set metadata fields that require premium user checks

    Args:
        object_data: The team data object to modify
        field_name: Name of the metadata field to set
        value: Value to set for the field
    """
    if field_name in MishikaLLM_ManagementEndpoint_MetadataFields_Premium:
        _premium_user_check()
    object_data.metadata = object_data.metadata or {}
    object_data.metadata[field_name] = value
