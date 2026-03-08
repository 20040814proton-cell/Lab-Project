from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from models import InviteCode, Student, SuperAdmin, Teacher, UserRole
from routers._account_messages import AccountMessages
from routers._account_utils import (
    is_login_email_taken,
    is_username_taken,
    is_valid_username,
    normalize_login_email,
    normalize_username,
)
from routers.auth import get_password_hash
from routers._grade_policy import get_effective_grades
from schemas import GradeOptionsOut

router = APIRouter()


class RegisterRequest(BaseModel):
    name: str
    password: str
    role: Optional[str] = None  # Optional, validated by invite code role.
    grade: Optional[int] = None  # Required for student.
    invite_code: Optional[str] = None  # Required for all roles.
    login_email: EmailStr
    username: Optional[str] = None  # Optional for teacher/superadmin.


@router.get("/register/grade-options", response_model=GradeOptionsOut)
async def get_register_grade_options():
    grades, source = await get_effective_grades()
    return GradeOptionsOut(grades=grades, source=source)


@router.post("/register")
async def register(req: RegisterRequest):
    if not req.invite_code:
        raise HTTPException(status_code=400, detail=AccountMessages.INVITE_CODE_REQUIRED)

    invite = await InviteCode.find_one({"code": req.invite_code, "is_active": True})
    if not invite:
        raise HTTPException(status_code=403, detail=AccountMessages.INVITE_CODE_INVALID)
    if invite.expires_at and invite.expires_at < datetime.utcnow():
        raise HTTPException(status_code=403, detail=AccountMessages.INVITE_CODE_EXPIRED)
    if invite.used_count >= invite.max_uses:
        invite.is_active = False
        await invite.save()
        raise HTTPException(status_code=403, detail=AccountMessages.INVITE_CODE_EXHAUSTED)

    role = invite.role
    if req.role and req.role != role:
        raise HTTPException(status_code=400, detail=AccountMessages.INVITE_ROLE_MISMATCH)

    login_email = normalize_login_email(str(req.login_email))
    if not login_email:
        raise HTTPException(status_code=400, detail=AccountMessages.LOGIN_EMAIL_REQUIRED)
    if await is_login_email_taken(login_email):
        raise HTTPException(status_code=400, detail=AccountMessages.LOGIN_EMAIL_EXISTS)

    if role == UserRole.STUDENT:
        if not req.grade:
            raise HTTPException(status_code=400, detail=AccountMessages.STUDENT_GRADE_REQUIRED)

        allowed_grades, _ = await get_effective_grades()
        if req.grade not in allowed_grades:
            grade_list = ", ".join(str(g) for g in allowed_grades)
            raise HTTPException(
                status_code=400,
                detail=f"年级 {req.grade} 不在允许范围内，可选年级：{grade_list}。",
            )

        prefix = str(req.grade)
        latest_student = await Student.find({"username": {"$regex": f"^{prefix}"}}).sort("-username").limit(1).to_list()

        new_id_suffix = 1
        if latest_student and latest_student[0].username:
            try:
                current_suffix = int(latest_student[0].username[len(prefix):])
                new_id_suffix = current_suffix + 1
            except ValueError:
                pass

        new_username = f"{prefix}{new_id_suffix:03d}"
        while await is_username_taken(new_username):
            new_id_suffix += 1
            new_username = f"{prefix}{new_id_suffix:03d}"

        student = Student(
            username=new_username,
            login_email=login_email,
            password_hash=get_password_hash(req.password),
            name=req.name,
            grade=req.grade,
            role="Student",
            desc=f"{req.grade} Grade Student",
        )
        await student.insert()
        invite.used_count += 1
        if invite.used_count >= invite.max_uses:
            invite.is_active = False
        await invite.save()
        return {"status": "success", "username": new_username, "message": f"学生注册成功，账号：{new_username}"}

    if role == UserRole.TEACHER:
        username = normalize_username(req.username or "")
        if not username:
            base = "teacher"
            index = int(datetime.utcnow().timestamp())
            username = f"{base}{index}"
            while await is_username_taken(username):
                index += 1
                username = f"{base}{index}"
        elif not is_valid_username(username):
            raise HTTPException(status_code=400, detail=AccountMessages.USERNAME_INVALID)

        if await is_username_taken(username):
            raise HTTPException(status_code=400, detail=AccountMessages.USERNAME_EXISTS)

        teacher = Teacher(
            username=username,
            login_email=login_email,
            password_hash=get_password_hash(req.password),
            name=req.name,
            role="Teacher",
            desc="Lab Teacher",
        )
        await teacher.insert()
        invite.used_count += 1
        if invite.used_count >= invite.max_uses:
            invite.is_active = False
        await invite.save()
        return {"status": "success", "username": username, "message": "教师注册成功"}

    if role == UserRole.SUPERADMIN:
        username = normalize_username(req.username or "")
        if not username:
            base = "superadmin"
            index = int(datetime.utcnow().timestamp())
            username = f"{base}{index}"
            while await is_username_taken(username):
                index += 1
                username = f"{base}{index}"
        elif not is_valid_username(username):
            raise HTTPException(status_code=400, detail=AccountMessages.USERNAME_INVALID)

        if await is_username_taken(username):
            raise HTTPException(status_code=400, detail=AccountMessages.USERNAME_EXISTS)

        admin = SuperAdmin(
            username=username,
            login_email=login_email,
            password_hash=get_password_hash(req.password),
            name=req.name,
            role="Superadmin",
            desc="Super Admin",
        )
        await admin.insert()
        invite.used_count += 1
        if invite.used_count >= invite.max_uses:
            invite.is_active = False
        await invite.save()
        return {"status": "success", "username": username, "message": "超级管理员注册成功"}

    raise HTTPException(status_code=400, detail=AccountMessages.INVALID_ROLE)
