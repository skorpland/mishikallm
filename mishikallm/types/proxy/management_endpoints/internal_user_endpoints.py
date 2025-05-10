from typing import Any, Dict, List, Literal, Optional, Union

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr

from mishikallm.proxy._types import MishikaLLM_UserTableWithKeyCount


class UserListResponse(BaseModel):
    """
    Response model for the user list endpoint
    """

    users: List[MishikaLLM_UserTableWithKeyCount]
    total: int
    page: int
    page_size: int
    total_pages: int
