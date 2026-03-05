from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Union
from models import Student, Teacher, SuperAdmin, UserRole
from schemas import StudentOut, TeacherOut, SuperAdminOut, UserUpdate, PublicUserOut
from routers.auth import get_current_user

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
    )

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
