from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from models import Post, UserRole
from schemas import PostAdjacentOut, PostCreate, PostOut, PostUpdate
from routers.auth import get_current_user
from beanie import PydanticObjectId

router = APIRouter()

@router.get("/", response_model=List[PostOut])
async def get_posts(
    q: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
):
    query = {}
    if q:
        query = {
            "$or": [
                {"title": {"$regex": q, "$options": "i"}},
                {"summary": {"$regex": q, "$options": "i"}},
                {"content": {"$regex": q, "$options": "i"}},
            ]
        }
    skip = (page - 1) * page_size
    return await Post.find(query).sort("-date").skip(skip).limit(page_size).to_list()

@router.get("/{id}", response_model=PostOut)
async def get_post(id: PydanticObjectId):
    post = await Post.get(id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.get("/{id}/adjacent", response_model=PostAdjacentOut)
async def get_post_adjacent(id: PydanticObjectId):
    post = await Post.get(id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    previous_list = await Post.find({"date": {"$lt": post.date}}).sort("-date").limit(1).to_list()
    next_list = await Post.find({"date": {"$gt": post.date}}).sort("date").limit(1).to_list()

    previous = previous_list[0] if previous_list else None
    next_post = next_list[0] if next_list else None

    return {
        "previous": (
            {
                "id": previous.id,
                "title": previous.title,
                "date": previous.date,
            }
            if previous
            else None
        ),
        "next": (
            {
                "id": next_post.id,
                "title": next_post.title,
                "date": next_post.date,
            }
            if next_post
            else None
        ),
    }

@router.post("/", response_model=PostOut)
async def create_post(post: PostCreate, current_user: dict = Depends(get_current_user)):
    if current_user['role'] not in [UserRole.TEACHER, UserRole.SUPERADMIN]:
        raise HTTPException(status_code=403, detail="Only teachers can create posts")
        
    # Create Post with Author from current_user
    new_post = Post(
        **post.dict(), 
        author=current_user.get('username', 'Teacher') # Or fetch name if available, for now username
    )
    await new_post.insert()
    return new_post

@router.put("/{id}", response_model=PostOut)
async def update_post(id: PydanticObjectId, req: PostUpdate, current_user: dict = Depends(get_current_user)):
    role = current_user.get('role')
    # Use loose check matching other endpoints, or strictly strict?
    # Let's use the explicit list for consistency with other parts of system
    allowed = [UserRole.TEACHER, UserRole.SUPERADMIN, "admin", "professor", "Admin", "Professor", UserRole.TEACHER.value]
    
    if str(role) not in [str(r) for r in allowed]: # Simple string comparison
         raise HTTPException(status_code=403, detail="Permission denied")

    post = await Post.get(id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Update fields
    req_dict = req.dict(exclude_unset=True)
    if req_dict:
        await post.set(req_dict)
    
    return post

@router.delete("/{id}")
async def delete_post(id: PydanticObjectId, current_user: dict = Depends(get_current_user)):
    if current_user['role'] not in [UserRole.TEACHER, UserRole.SUPERADMIN]:
        raise HTTPException(status_code=403, detail="Permission denied")
        
    post = await Post.get(id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    await post.delete()
    return {"status": "deleted"}
