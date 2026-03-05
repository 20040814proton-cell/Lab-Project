from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from models import SuperAdmin, UserRole
from routers.auth import get_current_user, get_password_hash

router = APIRouter()

class SuperAdminCreate(BaseModel):
    username: str
    name: str
    password: str

def require_superadmin(current_user: dict):
    if current_user.get('role') != UserRole.SUPERADMIN:
        raise HTTPException(status_code=403, detail="Superadmin only")

@router.post("/superadmins")
async def create_superadmin(req: SuperAdminCreate, current_user: dict = Depends(get_current_user)):
    require_superadmin(current_user)
    if await SuperAdmin.find_one({"username": req.username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    admin = SuperAdmin(
        username=req.username,
        password_hash=get_password_hash(req.password),
        name=req.name,
        role="Superadmin",
        desc="Super Admin"
    )
    await admin.insert()
    return {"status": "success", "username": req.username}
