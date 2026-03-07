from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Union
from models import Student, Teacher, SuperAdmin, UserRole, ForumPost, ForumComment, Activity, Project, Software
from schemas import (
    StudentOut,
    TeacherOut,
    SuperAdminOut,
    UserUpdate,
    PublicUserOut,
    UserContributionsOut,
    ContributionCountsOut,
    ForumPostSummaryOut,
    ForumCommentSummaryOut,
    ActivitySummaryOut,
    ProjectSummaryOut,
    SoftwareSummaryOut,
)
from routers.auth import get_current_user
from beanie import PydanticObjectId

router = APIRouter()

async def find_user_by_username(username: str):
    user = await Teacher.find_one({"username": username})
    if user:
        return user
    user = await Student.find_one({"username": username})
    if user:
        return user
    return await SuperAdmin.find_one({"username": username})

def as_public_user(user) -> PublicUserOut:
    raw_user_role = getattr(user, 'user_role', '')
    normalized_user_role = raw_user_role.value if hasattr(raw_user_role, 'value') else str(raw_user_role)
    return PublicUserOut(
        username=user.username,
        name=user.name,
        user_role=normalized_user_role,
        role=getattr(user, 'role', None),
        avatar=getattr(user, 'avatar', None),
        bio=getattr(user, 'bio', None),
        major=getattr(user, 'major', None),
        interests=getattr(user, 'interests', []) or [],
        research_areas=getattr(user, 'research_areas', []) or [],
        public_email=getattr(user, 'public_email', None),
    )

def make_preview(text: str, max_len: int = 120) -> str:
    normalized = ' '.join((text or '').split())
    if len(normalized) <= max_len:
        return normalized
    return f"{normalized[:max_len]}..."

@router.get("/", response_model=List[Union[TeacherOut, StudentOut, SuperAdminOut]])
async def get_users(role: str = Query(None)):
    """
    Get users list. 
    If role='teacher', return teachers.
    If role='student', return students.
    If no role, return all (merged).
    """
    results = []
    
    # Fetch all users first (Safe Python Filter as requested)
    # Note: For large datasets this is inefficient, but fine for current scale.
    teachers = await Teacher.find_all().to_list()
    students = await Student.find_all().to_list()
    admins = await SuperAdmin.find_all().to_list()
    all_users = teachers + students + admins

    if role == 'teacher':
        # BROADER SEARCH: Include Professor, Admin, and Teacher
        target_roles = ["teacher", "professor", "admin"]
        # Case insensitive check
        results = [u for u in all_users if u.role and u.role.lower() in target_roles]
    elif role:
        # Standard strict filter
        results = [u for u in all_users if u.role == role]
    else:
        results = all_users
        
    return results

@router.get("/me", response_model=Union[TeacherOut, StudentOut, SuperAdminOut])
async def read_users_me(current_user: dict = Depends(get_current_user)):
    uid = current_user['id']
    role = current_user['role']

    if role == UserRole.TEACHER:
        user = await Teacher.get(uid)
    elif role == UserRole.STUDENT:
        user = await Student.get(uid)
    elif role == UserRole.SUPERADMIN:
        user = await SuperAdmin.get(uid)
    else:
        user = await Teacher.get(uid)

    if not user:
        user = await Student.get(uid)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

@router.put("/me", response_model=Union[TeacherOut, StudentOut, SuperAdminOut])
async def update_my_profile(req: UserUpdate, current_user: dict = Depends(get_current_user)):
    role = current_user['role']
    uid = current_user['id']

    user_doc = None
    if role == UserRole.STUDENT:
        user_doc = await Student.get(uid)
    elif role == UserRole.TEACHER:
        user_doc = await Teacher.get(uid)
    elif role == UserRole.SUPERADMIN:
        user_doc = await SuperAdmin.get(uid)

    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")

    await user_doc.set(req.dict(exclude_unset=True))
    return user_doc

@router.get("/public/{username}", response_model=PublicUserOut)
async def read_user_public_profile(username: str):
    user = await find_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return as_public_user(user)

@router.get("/public/{username}/contributions", response_model=UserContributionsOut)
async def read_user_contributions(username: str, limit: int = Query(5, ge=1, le=10)):
    user = await find_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_id = str(user.id)
    forum_query = {"$or": [{"author_id": user_id}, {"author_name": username}, {"author_id": username}]}

    forum_post_total = await ForumPost.find(forum_query).count()
    forum_comment_total = await ForumComment.find(forum_query).count()
    activity_total = await Activity.find({"created_by_username": username}).count()
    project_total = await Project.find({"created_by_username": username}).count()
    software_total = await Software.find({"created_by_username": username}).count()

    forum_posts = await ForumPost.find(forum_query).sort("-created_at").limit(limit).to_list()
    forum_comments = await ForumComment.find(forum_query).sort("-created_at").limit(limit).to_list()
    activities = await Activity.find({"created_by_username": username}).sort("-created_at").limit(limit).to_list()
    projects = await Project.find({"created_by_username": username}).sort("-created_at").limit(limit).to_list()
    software_items = await Software.find({"created_by_username": username}).sort("-upload_date").limit(limit).to_list()

    post_ids = []
    for comment in forum_comments:
        try:
            post_ids.append(PydanticObjectId(comment.post_id))
        except Exception:
            continue

    posts = await ForumPost.find({"_id": {"$in": post_ids}}).to_list() if post_ids else []
    post_title_map = {str(post.id): post.title for post in posts}

    return UserContributionsOut(
        counts=ContributionCountsOut(
            forum_posts=forum_post_total,
            forum_comments=forum_comment_total,
            activities=activity_total,
            projects=project_total,
            software=software_total,
        ),
        recent_forum_posts=[
            ForumPostSummaryOut(id=post.id, title=post.title, created_at=post.created_at)
            for post in forum_posts
        ],
        recent_forum_comments=[
            ForumCommentSummaryOut(
                id=comment.id,
                post_id=comment.post_id,
                post_title=post_title_map.get(comment.post_id, "Post deleted"),
                created_at=comment.created_at,
                content_preview=make_preview(comment.content),
            )
            for comment in forum_comments
        ],
        recent_activities=[
            ActivitySummaryOut(id=item.id, title=item.title, date=item.date, type=item.type)
            for item in activities
        ],
        recent_projects=[
            ProjectSummaryOut(id=item.id, title=item.title, status=item.status, created_at=item.created_at)
            for item in projects
        ],
        recent_software=[
            SoftwareSummaryOut(id=item.id, name=item.name, version=item.version, upload_date=item.upload_date)
            for item in software_items
        ],
    )
