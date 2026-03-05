from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from beanie import PydanticObjectId
from models import Software, UserRole
from routers.auth import get_current_user
from schemas import SoftwareCreate, SoftwareOut

router = APIRouter()

@router.get("/", response_model=List[SoftwareOut])
async def get_software():
    return await Software.find_all().sort("-upload_date").to_list()

@router.post("/", response_model=SoftwareOut)
async def create_software(payload: SoftwareCreate, current_user: dict = Depends(get_current_user)):
    # DEBUG LOG
    print(f"DEBUG: create_software called with payload: {payload}")
    print(f"DEBUG: Software model class is: {Software}")

    role = current_user.get('role')
    # Permission check for Faculty
    allowed = [UserRole.TEACHER.value, UserRole.SUPERADMIN.value, "admin", "professor"]
    
    # Check if role is allowed (case insensitive)
    if not role or str(role).lower() not in allowed:
        print(f"DEBUG: Permission denied for role: {role}")
        raise HTTPException(status_code=403, detail="Permission denied")
    
    # Create document
    # Ensure we are using the model class 'Software'
    new_software = Software(**payload.dict())
    await new_software.insert()
    return new_software

@router.delete("/{id}")
async def delete_software(id: PydanticObjectId, current_user: dict = Depends(get_current_user)):
    role = current_user.get('role')
    allowed = [UserRole.TEACHER.value, UserRole.SUPERADMIN.value, "admin", "professor"]
    
    if not role or str(role).lower() not in allowed:
         raise HTTPException(status_code=403, detail="Permission denied")
         
    sw = await Software.get(id)
    if not sw:
        raise HTTPException(status_code=404, detail="Software not found")
        
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
