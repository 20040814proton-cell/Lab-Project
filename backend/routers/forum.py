from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Tuple

from beanie import PydanticObjectId

from models import ForumPost, ForumComment, Student, Teacher, SuperAdmin, UserRole
from routers.auth import get_current_user
from schemas import (
    ForumPostCreate,
    ForumPostUpdate,
    ForumPostOut,
    ForumCommentCreate,
    ForumCommentUpdate,
    ForumCommentOut,
    ForumUserCommentOut,
)

router = APIRouter()


def can_moderate(current_user: dict):
    return current_user.get('role') in [UserRole.TEACHER, UserRole.SUPERADMIN]


async def find_user_by_id(user_id: Optional[str]):
    if not user_id:
        return None
    try:
        object_id = PydanticObjectId(user_id)
    except Exception:
        return None

    user = await Teacher.get(object_id)
    if user:
        return user
    user = await Student.get(object_id)
    if user:
        return user
    return await SuperAdmin.get(object_id)


async def find_user_by_username(username: str):
    user = await Teacher.find_one({"username": username})
    if user:
        return user
    user = await Student.find_one({"username": username})
    if user:
        return user
    return await SuperAdmin.find_one({"username": username})


async def resolve_author_identity(author_id: Optional[str], author_name: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    user = None
    if author_id:
        user = await find_user_by_id(author_id)
    if not user and author_name:
        user = await find_user_by_username(author_name)
    if not user and author_name:
        user = await find_user_by_id(author_name)
    if not user and author_id:
        user = await find_user_by_username(author_id)

    if user:
        username = getattr(user, "username", None)
        display_name = getattr(user, "name", None) or username
        return username, display_name

    fallback = author_name or author_id
    return fallback, fallback


async def normalize_author_name(doc) -> Tuple[Optional[str], Optional[str]]:
    username, display_name = await resolve_author_identity(
        getattr(doc, "author_id", None),
        getattr(doc, "author_name", None),
    )
    if username and getattr(doc, "author_name", None) != username:
        await doc.set({"author_name": username})
        doc.author_name = username
    return username, display_name


def serialize_post(post: ForumPost, display_name: Optional[str]) -> ForumPostOut:
    return ForumPostOut(
        id=post.id,
        title=post.title,
        content=post.content,
        tags=post.tags or [],
        author_id=post.author_id,
        author_name=post.author_name,
        author_display_name=display_name or post.author_name or post.author_id,
        created_at=post.created_at,
        is_pinned=post.is_pinned,
        is_featured=post.is_featured,
    )


def serialize_comment(comment: ForumComment, display_name: Optional[str]) -> ForumCommentOut:
    return ForumCommentOut(
        id=comment.id,
        post_id=comment.post_id,
        author_id=comment.author_id,
        author_name=comment.author_name,
        author_display_name=display_name or comment.author_name or comment.author_id,
        content=comment.content,
        created_at=comment.created_at,
    )


async def normalize_posts(posts: List[ForumPost]) -> List[ForumPostOut]:
    normalized: List[ForumPostOut] = []
    for post in posts:
        _, display_name = await normalize_author_name(post)
        normalized.append(serialize_post(post, display_name))
    return normalized


async def normalize_comments(comments: List[ForumComment]) -> List[ForumCommentOut]:
    normalized: List[ForumCommentOut] = []
    for comment in comments:
        _, display_name = await normalize_author_name(comment)
        normalized.append(serialize_comment(comment, display_name))
    return normalized


@router.get("/", response_model=List[ForumPostOut])
async def list_posts(
    q: Optional[str] = None,
    tag: Optional[str] = None,
    creator: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
):
    filters = []
    if q:
        filters.append({"$or": [{"title": {"$regex": q, "$options": "i"}}, {"content": {"$regex": q, "$options": "i"}}]})
    if tag:
        filters.append({"tags": tag})
    if creator:
        user = await find_user_by_username(creator)
        if user:
            filters.append({"$or": [{"author_id": str(user.id)}, {"author_name": creator}, {"author_id": creator}]})
        else:
            filters.append({"$or": [{"author_name": creator}, {"author_id": creator}]})
    query = {}
    if filters:
        query = {"$and": filters} if len(filters) > 1 else filters[0]

    skip = (page - 1) * page_size
    posts = await ForumPost.find(query).sort("-is_pinned", "-is_featured", "-created_at").skip(skip).limit(page_size).to_list()
    return await normalize_posts(posts)


@router.get("/tags", response_model=List[str])
async def list_tags():
    posts = await ForumPost.find_all().to_list()
    tag_set = set()
    for post in posts:
        for tag in (post.tags or []):
            tag_set.add(tag)
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

    filters = [{"$or": [{"author_id": str(user.id)}, {"author_name": username}, {"author_id": username}]}]
    if q:
        filters.append({"$or": [{"title": {"$regex": q, "$options": "i"}}, {"content": {"$regex": q, "$options": "i"}}]})
    if tag:
        filters.append({"tags": tag})

    query = {"$and": filters} if len(filters) > 1 else filters[0]
    skip = (page - 1) * page_size
    posts = await ForumPost.find(query).sort("-is_pinned", "-is_featured", "-created_at").skip(skip).limit(page_size).to_list()
    return await normalize_posts(posts)


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

    filters = [{"$or": [{"author_id": str(user.id)}, {"author_name": username}, {"author_id": username}]}]
    if q:
        filters.append({"content": {"$regex": q, "$options": "i"}})

    query = {"$and": filters} if len(filters) > 1 else filters[0]
    skip = (page - 1) * page_size
    comments = await ForumComment.find(query).sort("-created_at").skip(skip).limit(page_size).to_list()

    display_name_map = {}
    for comment in comments:
        _, display_name = await normalize_author_name(comment)
        display_name_map[str(comment.id)] = display_name or comment.author_name or comment.author_id

    post_ids = list({comment.post_id for comment in comments})
    valid_post_ids = []
    for post_id in post_ids:
        try:
            valid_post_ids.append(PydanticObjectId(post_id))
        except Exception:
            continue

    posts = await ForumPost.find({"_id": {"$in": valid_post_ids}}).to_list() if valid_post_ids else []
    post_title_map = {str(post.id): post.title for post in posts}

    return [
        ForumUserCommentOut(
            id=comment.id,
            post_id=comment.post_id,
            post_title=post_title_map.get(comment.post_id, "Post deleted"),
            author_id=comment.author_id,
            author_name=comment.author_name,
            author_display_name=display_name_map.get(str(comment.id), comment.author_name or comment.author_id),
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
    _, display_name = await normalize_author_name(post)
    return serialize_post(post, display_name)


@router.get("/{post_id}", response_model=ForumPostOut)
async def get_post(post_id: PydanticObjectId):
    post = await ForumPost.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    _, display_name = await normalize_author_name(post)
    return serialize_post(post, display_name)


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
        post = await ForumPost.get(post_id) or post

    _, display_name = await normalize_author_name(post)
    return serialize_post(post, display_name)


@router.get("/{post_id}/comments", response_model=List[ForumCommentOut])
async def list_comments(
    post_id: PydanticObjectId,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
):
    skip = (page - 1) * page_size
    comments = await ForumComment.find({"post_id": str(post_id)}).sort("created_at").skip(skip).limit(page_size).to_list()
    return await normalize_comments(comments)


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
    _, display_name = await normalize_author_name(comment)
    return serialize_comment(comment, display_name)


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
        comment = await ForumComment.get(comment_id) or comment

    _, display_name = await normalize_author_name(comment)
    return serialize_comment(comment, display_name)
