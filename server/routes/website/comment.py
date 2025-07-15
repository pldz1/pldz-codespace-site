from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from scripts.mongodb import AuthorizedHandler
from scripts.mongodb import CommentHandler

COMMENTS_ROUTE = APIRouter(prefix="/website/comment", tags=["website-comments"])


class AllCommentsRequest(BaseModel):
    article_id: str


@COMMENTS_ROUTE.post("/all")
async def api_get_article_comments(request: AllCommentsRequest):
    """
    获取指定文章的所有评论
    :param article_id: 文章的唯一ID
    :return: 评论列表
    """
    article_id = request.article_id
    if not article_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Article ID is required."
        )
    data = CommentHandler.get_all_comments_by_id(article_id)
    return {'data': data}


class AddCommentRequest(BaseModel):
    article_id: str
    content: dict
    parent_id: str


@COMMENTS_ROUTE.post("/add")
async def api_add_comment(request: AddCommentRequest, user: dict = Depends(AuthorizedHandler.get_current_user)):
    """
    添加评论
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be logged in to add comments."
        )

    username = user.get('username')
    isadmin = AuthorizedHandler.check_admin(username)
    if not isadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to sync articles."
        )
    flag = CommentHandler.add_comment(request.article_id, request.content, request.parent_id)
    return {"data": flag}


class DeleteCommentRequest(BaseModel):
    article_id: str
    comment_id: str


@COMMENTS_ROUTE.post("/delete")
async def api_delete_comment(request: DeleteCommentRequest, user: dict = Depends(AuthorizedHandler.get_current_user)):
    """
    删除评论
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be logged in to delete comments."
        )

    username = user.get('username')
    isadmin = AuthorizedHandler.check_admin(username)
    if not isadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete comments."
        )

    flag = CommentHandler.delete_comment(request.article_id, request.comment_id)
    return {"data": flag}
