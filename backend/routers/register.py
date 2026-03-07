from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models import Student, Teacher, SuperAdmin, InviteCode, UserRole
from routers.auth import get_password_hash
from routers._grade_policy import get_effective_grades
from schemas import GradeOptionsOut

router = APIRouter()

class RegisterRequest(BaseModel):
    name: str
    password: str
    role: Optional[str] = None # optional, will be validated by invite
    grade: Optional[int] = None # Required for student
    invite_code: Optional[str] = None # Required for all roles
    username: Optional[str] = None # Optional for teacher (if they want custom), auto-generated for student

@router.get("/register/grade-options", response_model=GradeOptionsOut)
async def get_register_grade_options():
    grades, source = await get_effective_grades()
    return GradeOptionsOut(grades=grades, source=source)

@router.post("/register")
async def register(req: RegisterRequest):
    if not req.invite_code:
        raise HTTPException(status_code=400, detail="Invite code is required")

    invite = await InviteCode.find_one({"code": req.invite_code, "is_active": True})
    if not invite:
        raise HTTPException(status_code=403, detail="Invalid invite code")
    if invite.expires_at and invite.expires_at < datetime.utcnow():
        raise HTTPException(status_code=403, detail="Invite code expired")
    if invite.used_count >= invite.max_uses:
        invite.is_active = False
        await invite.save()
        raise HTTPException(status_code=403, detail="Invite code has no remaining uses")

    role = invite.role
    if req.role and req.role != role:
        raise HTTPException(status_code=400, detail="Invite role mismatch")

    if role == UserRole.STUDENT:
        if not req.grade:
            raise HTTPException(status_code=400, detail="Student must provide grade (e.g. 2025)")

        allowed_grades, _ = await get_effective_grades()
        if req.grade not in allowed_grades:
            raise HTTPException(
                status_code=400,
                detail=f"Grade {req.grade} is not allowed. Allowed grades: {', '.join(str(g) for g in allowed_grades)}",
            )
        
        # Smart ID Generation
        # Find latest student in this grade
        # Regex: Starts with str(grade)
        prefix = str(req.grade)
        # Sort by username descending to get the latest
        latest_student = await Student.find({"username": {"$regex": f"^{prefix}"}}).sort("-username").limit(1).to_list()
        
        new_id_suffix = 1
        if latest_student and latest_student[0].username:
            try:
                # e.g. 2025005 -> 5
                current_suffix = int(latest_student[0].username[len(prefix):])
                new_id_suffix = current_suffix + 1
            except ValueError:
                pass # Fallback to 1 if parsing fails
        
        # Format: 2025001 (3 digits padding)
        new_username = f"{prefix}{new_id_suffix:03d}"
        
        student = Student(
            username=new_username,
            password_hash=get_password_hash(req.password),
            name=req.name,
            grade=req.grade,
            role="Student",
            desc=f"{req.grade} Grade Student"
        )
        await student.insert()
        invite.used_count += 1
        if invite.used_count >= invite.max_uses:
            invite.is_active = False
        await invite.save()
        return {"status": "success", "username": new_username, "message": f"Student registered with ID: {new_username}"}

    elif role == UserRole.TEACHER:
        # Use provided username or name
        username = req.username or req.name
        
        # Check existence
        if await Teacher.find_one({"username": username}):
             raise HTTPException(status_code=400, detail="Username already exists")

        teacher = Teacher(
            username=username,
            password_hash=get_password_hash(req.password),
            name=req.name,
            role="Teacher",
            desc="Lab Teacher"
        )
        await teacher.insert()
        invite.used_count += 1
        if invite.used_count >= invite.max_uses:
            invite.is_active = False
        await invite.save()
        return {"status": "success", "username": username, "message": "Teacher registered successfully"}

    elif role == UserRole.SUPERADMIN:
        username = req.username or req.name
        if await SuperAdmin.find_one({"username": username}):
            raise HTTPException(status_code=400, detail="Username already exists")

        admin = SuperAdmin(
            username=username,
            password_hash=get_password_hash(req.password),
            name=req.name,
            role="Superadmin",
            desc="Super Admin"
        )
        await admin.insert()
        invite.used_count += 1
        if invite.used_count >= invite.max_uses:
            invite.is_active = False
        await invite.save()
        return {"status": "success", "username": username, "message": "Superadmin registered successfully"}
    
    raise HTTPException(status_code=400, detail="Invalid role")
