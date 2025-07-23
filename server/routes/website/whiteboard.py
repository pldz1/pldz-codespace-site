from pydantic import BaseModel
from typing import Optional, Any
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from scripts.mongodb import AuthorizedHandler
from scripts.mongodb import WhiteBoardHandler

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


@WHITEBOARD_ROUTE.post("/authorized")
async def api_get_whiteboard_by_username(user: dict = Depends(AuthorizedHandler.get_current_user)):
    """
    获取当前用户的白板内容
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be logged in to access your whiteboard."
        )

    username = user.get('username')
    item = WhiteBoardHandler.get_item_by_username(username)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Whiteboard item not found for the current user."
        )

    return {"data": item}


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
