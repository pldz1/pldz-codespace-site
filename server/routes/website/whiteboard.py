from pydantic import BaseModel
from typing import Optional, Any
from fastapi import HTTPException, Request, status
from fastapi.routing import APIRouter
from scripts.mongodb import AuthorizedHandler
from scripts.whiteboard import WhiteBoardHandler

WHITEBOARD_ROUTE = APIRouter(prefix="/website/whiteboard", tags=["website-whiteboard"])


"""
==========================
Get Whiteboard by Key
==========================
"""


class GetWhiteBoardByKeyRequest(BaseModel):
    key: str


@WHITEBOARD_ROUTE.post("/key")
async def api_get_whiteboard_by_key(request: GetWhiteBoardByKeyRequest):
    """
    根据键获取白板内容
    """
    if not request.key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Key is required."
        )

    item = WhiteBoardHandler.get_item_by_key(request.key)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Whiteboard item not found."
        )

    return {"data": item}


"""
===========================
Get Whiteboard by Username
===========================
"""


class GetWhiteBoardByUsernameRequest(BaseModel):
    username: Optional[str] = None
    create_new: bool = True


@WHITEBOARD_ROUTE.post("/authorized")
async def api_get_whiteboard_by_username(request: GetWhiteBoardByUsernameRequest, fastapi_request: Request):
    """
    获取当前用户（或指定用户名）的白板内容列表
    """
    username = (request.username or "").strip()

    if not username:
        try:
            user = AuthorizedHandler.get_current_user(fastapi_request)
            username = user.get('username', '') if user else ""
        except HTTPException as exc:
            if exc.status_code not in (status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND):
                raise
            username = ""

    items = WhiteBoardHandler.get_items_by_username(username, create_new=request.create_new)
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Whiteboard items not found."
        )

    return {"data": items}


"""
=========================
Update Request and Response Models
=========================
"""


class UpdateRequest(BaseModel):
    key: str
    content: str


class UpdateResponseData(BaseModel):
    flag: bool
    log: str
    created: Optional[Any] = None


class UpdateResponse(BaseModel):
    data: UpdateResponseData


@WHITEBOARD_ROUTE.post("/update")
async def api_update_whiteboard_content(request: UpdateRequest) -> UpdateResponse:
    """
    更新白板内容
    """
    if not request.key.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Key is required."
        )

    created = WhiteBoardHandler.set_content_by_key(request.key, request.content)

    if not created:
        return UpdateResponse(
            data=UpdateResponseData(
                flag=False,
                log="Failed to update whiteboard content."
            )
        )

    return UpdateResponse(
        data=UpdateResponseData(
            flag=True,
            log="Whiteboard content updated successfully.",
            created=created
        )
    )
