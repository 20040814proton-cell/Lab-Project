from datetime import datetime, timezone
import secrets
import string
from fastapi import APIRouter, Depends, HTTPException, Query
from models import InviteCode, RegistrationGradePolicy, UserRole
from schemas import (
    GradePolicyOut,
    GradePolicyUpdate,
    InviteCreate,
    InviteOut,
    PasswordResetByAdminIn,
    PasswordResetByAdminOut,
)
from routers.auth import get_current_user, get_password_hash
from routers._account_messages import AccountMessages
from routers._account_utils import (
    find_user_by_login_identifier,
    find_user_by_name_identifier,
    normalize_username,
)
from routers._grade_policy import POLICY_KEY, get_effective_grades, normalize_grades

router = APIRouter()

def require_superadmin(current_user: dict):
    if current_user.get('role') != UserRole.SUPERADMIN:
        raise HTTPException(status_code=403, detail=AccountMessages.SUPERADMIN_ONLY)


def generate_temp_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

@router.get("/", response_model=list[InviteOut])
async def list_invites(
    include_inactive: bool = Query(False),
    current_user: dict = Depends(get_current_user),
):
    require_superadmin(current_user)
    if include_inactive:
        return await InviteCode.find_all().sort("-created_at").to_list()
    return await InviteCode.find(InviteCode.is_active == True).sort("-created_at").to_list()

@router.post("/", response_model=InviteOut)
async def create_invite(req: InviteCreate, current_user: dict = Depends(get_current_user)):
    require_superadmin(current_user)
    try:
        role = UserRole(req.role)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid role")
    if req.max_uses <= 0:
        raise HTTPException(status_code=400, detail="max_uses must be > 0")
    if req.expires_at:
        if req.expires_at.tzinfo is None:
            now = datetime.utcnow()
        else:
            now = datetime.now(timezone.utc)
        if req.expires_at < now:
            raise HTTPException(status_code=400, detail="expires_at must be in the future")

    code = secrets.token_urlsafe(8)
    invite = InviteCode(
        code=code,
        role=role,
        max_uses=req.max_uses,
        used_count=0,
        expires_at=req.expires_at,
        note=req.note,
        created_by=current_user.get('username'),
    )
    await invite.insert()
    return invite

@router.delete("/{invite_id}")
async def delete_invite(invite_id: str, current_user: dict = Depends(get_current_user)):
    require_superadmin(current_user)
    invite = await InviteCode.get(invite_id)
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")
    invite.is_active = False
    await invite.save()
    return {"status": "deleted"}


@router.get("/grade-policy", response_model=GradePolicyOut)
async def get_grade_policy(current_user: dict = Depends(get_current_user)):
    require_superadmin(current_user)
    policy = await RegistrationGradePolicy.find_one({"policy_key": POLICY_KEY})
    effective_grades, source = await get_effective_grades()
    return GradePolicyOut(
        allowed_grades=normalize_grades(policy.allowed_grades if policy else []),
        effective_grades=effective_grades,
        source=source,
        updated_by=(policy.updated_by if policy else None),
        updated_at=(policy.updated_at if policy else None),
    )


@router.put("/grade-policy", response_model=GradePolicyOut)
async def update_grade_policy(req: GradePolicyUpdate, current_user: dict = Depends(get_current_user)):
    require_superadmin(current_user)
    grades = normalize_grades(req.allowed_grades)
    policy = await RegistrationGradePolicy.find_one({"policy_key": POLICY_KEY})
    if not policy:
        policy = RegistrationGradePolicy(
            policy_key=POLICY_KEY,
            allowed_grades=grades,
            updated_by=current_user.get("username"),
            updated_at=datetime.now(timezone.utc),
        )
        await policy.insert()
    else:
        policy.allowed_grades = grades
        policy.updated_by = current_user.get("username")
        policy.updated_at = datetime.now(timezone.utc)
        await policy.save()

    effective_grades, source = await get_effective_grades()
    return GradePolicyOut(
        allowed_grades=grades,
        effective_grades=effective_grades,
        source=source,
        updated_by=policy.updated_by,
        updated_at=policy.updated_at,
    )


@router.post("/password-reset", response_model=PasswordResetByAdminOut)
async def reset_user_password(req: PasswordResetByAdminIn, current_user: dict = Depends(get_current_user)):
    require_superadmin(current_user)

    identifier = normalize_username(req.identifier)
    if not identifier:
        raise HTTPException(status_code=400, detail=AccountMessages.PASSWORD_RESET_IDENTIFIER_REQUIRED)

    try:
        target_role = UserRole(req.role)
    except Exception:
        raise HTTPException(status_code=400, detail=AccountMessages.INVALID_ROLE)

    user = await find_user_by_login_identifier(target_role, identifier)
    if not user:
        user, name_duplicated = await find_user_by_name_identifier(target_role, identifier)
        if name_duplicated:
            raise HTTPException(status_code=400, detail=AccountMessages.LOGIN_NAME_DUPLICATE)
    if not user:
        raise HTTPException(status_code=404, detail=AccountMessages.USER_NOT_FOUND)

    temp_password = generate_temp_password()
    await user.set({
        "password_hash": get_password_hash(temp_password),
        "must_change_password": True,
        "password_reset_at": datetime.now(timezone.utc),
    })

    return PasswordResetByAdminOut(
        username=str(getattr(user, "username", "")),
        temp_password=temp_password,
        must_change_password=True,
    )
