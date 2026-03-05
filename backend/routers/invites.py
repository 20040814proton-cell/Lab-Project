from datetime import datetime, timezone
import secrets
from fastapi import APIRouter, Depends, HTTPException, Query
from models import InviteCode, UserRole
from schemas import InviteCreate, InviteOut
from routers.auth import get_current_user

router = APIRouter()

def require_superadmin(current_user: dict):
    if current_user.get('role') != UserRole.SUPERADMIN:
        raise HTTPException(status_code=403, detail="Superadmin only")

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
