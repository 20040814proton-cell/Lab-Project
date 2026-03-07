from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from beanie import PydanticObjectId
from models import Software, UserRole
from routers.auth import get_current_user
from schemas import SoftwareCreate, SoftwareOut, SoftwareUpdate

router = APIRouter()

def is_manager(current_user: dict) -> bool:
    return current_user.get("role") in [UserRole.TEACHER, UserRole.SUPERADMIN]

def is_owner(current_user: dict, software: Software) -> bool:
    owner_id = getattr(software, "created_by_id", None)
    return bool(owner_id) and str(owner_id) == str(current_user.get("id"))

def can_manage(current_user: dict, software: Software) -> bool:
    return is_manager(current_user) or is_owner(current_user, software)

@router.get("/", response_model=List[SoftwareOut])
async def get_software(creator: Optional[str] = Query(None)):
    if creator:
        return await Software.find({"created_by_username": creator}).sort("-upload_date").to_list()
    return await Software.find_all().sort("-upload_date").to_list()

@router.post("/", response_model=SoftwareOut)
async def create_software(payload: SoftwareCreate, current_user: dict = Depends(get_current_user)):
    new_software = Software(
        **payload.dict(),
        created_by_id=str(current_user["id"]),
        created_by_username=current_user.get("username"),
    )
    await new_software.insert()
    return new_software

@router.put("/{id}", response_model=SoftwareOut)
async def update_software(id: PydanticObjectId, payload: SoftwareUpdate, current_user: dict = Depends(get_current_user)):
    sw = await Software.get(id)
    if not sw:
        raise HTTPException(status_code=404, detail="Software not found")

    if not can_manage(current_user, sw):
        raise HTTPException(status_code=403, detail="Permission denied")

    update_data = payload.dict(exclude_unset=True)
    if update_data:
        await sw.set(update_data)
    return sw

@router.delete("/{id}")
async def delete_software(id: PydanticObjectId, current_user: dict = Depends(get_current_user)):
    sw = await Software.get(id)
    if not sw:
        raise HTTPException(status_code=404, detail="Software not found")

    if not can_manage(current_user, sw):
        raise HTTPException(status_code=403, detail="Permission denied")

    await sw.delete()
    return {"status": "deleted"}

@router.post("/{id}/download")
async def download_software(id: PydanticObjectId):
    sw = await Software.get(id)
    if not sw:
        raise HTTPException(status_code=404, detail="Software not found")

    sw.download_count += 1
    await sw.save()
    return {"status": "counted"}
