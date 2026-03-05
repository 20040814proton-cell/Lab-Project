from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from models import ForumPost, ForumComment, Student, Teacher, SuperAdmin, UserRole
from schemas import (
    ForumPostCreate,
    ForumPostUpdate,
    ForumPostOut,
    ForumCommentCreate,
    ForumCommentUpdate,
    ForumCommentOut,
    ForumUserCommentOut,
)
from routers.auth import get_current_user
from beanie import PydanticObjectId

router = APIRouter()

def can_moderate(current_user: dict):
    return current_user.get('role') in [UserRole.TEACHER, UserRole.SUPERADMIN]

async def find_user_by_username(username: str):
    user = await Teacher.find_one({"username": username})
    if user:
        return user
    user = await Student.find_one({"username": username})
    if user:
        return user
    return await SuperAdmin.find_one({"username": username})

@router.get("/", response_model=List[ForumPostOut])
async def list_posts(
    q: Optional[str] = None,
    tag: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
):
    filters = []
    if q:
        filters.append({"$or": [{"title": {"$regex": q, "$options": "i"}}, {"content": {"$regex": q, "$options": "i"}}]})
    if tag:
        filters.append({"tags": tag})
    query = {}
    if filters:
        query = {"$and": filters} if len(filters) > 1 else filters[0]
    skip = (page - 1) * page_size
    return await ForumPost.find(query).sort("-is_pinned", "-is_featured", "-created_at").skip(skip).limit(page_size).to_list()

@router.get("/tags", response_model=List[str])
async def list_tags():
    posts = await ForumPost.find_all().to_list()
    tag_set = set()
    for p in posts:
        for t in (p.tags or []):
            tag_set.add(t)
    return sorted(tag_set)

@router.get("/users/{username}/posts", response_model=List[ForumPostOut])
async def list_user_posts(
    username: str,
    q: Optional[str] = None,
    tag: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
):
    user = await find_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    filters = [{"$or": [{"author_id": str(user.id)}, {"author_name": username}]}]
    if q:
        filters.append({"$or": [{"title": {"$regex": q, "$options": "i"}}, {"content": {"$regex": q, "$options": "i"}}]})
    if tag:
        filters.append({"tags": tag})

    query = {"$and": filters} if len(filters) > 1 else filters[0]
    skip = (page - 1) * page_size
    return await ForumPost.find(query).sort("-is_pinned", "-is_featured", "-created_at").skip(skip).limit(page_size).to_list()

@router.get("/users/{username}/comments", response_model=List[ForumUserCommentOut])
async def list_user_comments(
    username: str,
    q: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
):
    user = await find_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    filters = [{"$or": [{"author_id": str(user.id)}, {"author_name": username}]}]
    if q:
        filters.append({"content": {"$regex": q, "$options": "i"}})

    query = {"$and": filters} if len(filters) > 1 else filters[0]
    skip = (page - 1) * page_size
    comments = await ForumComment.find(query).sort("-created_at").skip(skip).limit(page_size).to_list()
    post_ids = list({comment.post_id for comment in comments})
    valid_post_ids = []
    for pid in post_ids:
        try:
            valid_post_ids.append(PydanticObjectId(pid))
        except Exception:
            continue
    posts = await ForumPost.find({"_id": {"$in": valid_post_ids}}).to_list() if valid_post_ids else []
    post_title_map = {str(post.id): post.title for post in posts}

    return [
        ForumUserCommentOut(
            id=comment.id,
            post_id=comment.post_id,
            post_title=post_title_map.get(comment.post_id, "帖子已删除"),
            author_id=comment.author_id,
            author_name=comment.author_name,
            content=comment.content,
            created_at=comment.created_at,
        )
        for comment in comments
    ]

@router.post("/", response_model=ForumPostOut)
async def create_post(req: ForumPostCreate, current_user: dict = Depends(get_current_user)):
    post = ForumPost(
        **req.dict(),
        author_id=str(current_user['id']),
        author_name=current_user.get('username'),
    )
    await post.insert()
    return post

@router.get("/{post_id}", response_model=ForumPostOut)
async def get_post(post_id: PydanticObjectId):
    post = await ForumPost.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.delete("/{post_id}")
async def delete_post(post_id: PydanticObjectId, current_user: dict = Depends(get_current_user)):
    post = await ForumPost.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if str(post.author_id) != str(current_user['id']) and not can_moderate(current_user):
        raise HTTPException(status_code=403, detail="Permission denied")
    await post.delete()
    return {"status": "deleted"}

@router.patch("/{post_id}", response_model=ForumPostOut)
async def update_post(post_id: PydanticObjectId, req: ForumPostUpdate, current_user: dict = Depends(get_current_user)):
    post = await ForumPost.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if str(post.author_id) != str(current_user['id']) and not can_moderate(current_user):
        raise HTTPException(status_code=403, detail="Permission denied")
    update_data = {k: v for k, v in req.dict().items() if v is not None}
    if not can_moderate(current_user):
        update_data.pop("is_pinned", None)
        update_data.pop("is_featured", None)
    if update_data:
        await post.set(update_data)
    return post

@router.get("/{post_id}/comments", response_model=List[ForumCommentOut])
async def list_comments(
    post_id: PydanticObjectId,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
):
    skip = (page - 1) * page_size
    return await ForumComment.find({"post_id": str(post_id)}).sort("created_at").skip(skip).limit(page_size).to_list()

@router.post("/{post_id}/comments", response_model=ForumCommentOut)
async def create_comment(post_id: PydanticObjectId, req: ForumCommentCreate, current_user: dict = Depends(get_current_user)):
    post = await ForumPost.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    comment = ForumComment(
        post_id=str(post_id),
        author_id=str(current_user['id']),
        author_name=current_user.get('username'),
        content=req.content,
    )
    await comment.insert()
    return comment

@router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: PydanticObjectId, current_user: dict = Depends(get_current_user)):
    comment = await ForumComment.get(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if str(comment.author_id) != str(current_user['id']) and not can_moderate(current_user):
        raise HTTPException(status_code=403, detail="Permission denied")
    await comment.delete()
    return {"status": "deleted"}

@router.patch("/comments/{comment_id}", response_model=ForumCommentOut)
async def update_comment(comment_id: PydanticObjectId, req: ForumCommentUpdate, current_user: dict = Depends(get_current_user)):
    comment = await ForumComment.get(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if str(comment.author_id) != str(current_user['id']) and not can_moderate(current_user):
        raise HTTPException(status_code=403, detail="Permission denied")
    update_data = {k: v for k, v in req.dict().items() if v is not None}
    if update_data:
        await comment.set(update_data)
    return comment
