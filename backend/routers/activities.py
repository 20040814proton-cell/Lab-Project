from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from models import Activity, UserRole
from schemas import ActivityCreate, ActivityOut, ActivityUpdate
from routers.auth import get_current_user
from beanie import PydanticObjectId, operators

router = APIRouter()

@router.get("/", response_model=List[ActivityOut])
async def get_activities():
    return await Activity.find_all().sort("-date").to_list()

@router.get("/stats")
async def get_stats():
    # Specific counts for Ink Dashboard
    workshops = await Activity.find({"type": "工作坊"}).count()
    seminars = await Activity.find({"type": "研讨会"}).count()
    opendays = await Activity.find({"type": "开放日"}).count()
    
    return {
        "研讨会": seminars,
        "工作坊": workshops,
        "开放日": opendays
    }

@router.get("/{id}", response_model=ActivityOut)
async def get_activity(id: PydanticObjectId):
    act = await Activity.get(id)
    if not act:
        raise HTTPException(status_code=404, detail="Activity not found")
    return act

@router.post("/", response_model=ActivityOut)
async def create_activity(activity: ActivityCreate, current_user: dict = Depends(get_current_user)):
    if current_user['role'] not in [UserRole.TEACHER, UserRole.SUPERADMIN]:
        raise HTTPException(status_code=403, detail="Only teachers can create activities")
    
    new_activity = Activity(**activity.dict())
    await new_activity.insert()
    return new_activity

@router.put("/{id}", response_model=ActivityOut)
async def update_activity(id: PydanticObjectId, req: ActivityUpdate, current_user: dict = Depends(get_current_user)):
    if current_user['role'] not in [UserRole.TEACHER, UserRole.SUPERADMIN]:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    act = await Activity.get(id)
    if not act:
        raise HTTPException(status_code=404, detail="Activity not found")
        
    await act.set(req.dict(exclude_unset=True))
    return act

@router.delete("/{id}")
async def delete_activity(id: PydanticObjectId, current_user: dict = Depends(get_current_user)):
    if current_user['role'] not in [UserRole.TEACHER, UserRole.SUPERADMIN]:
        raise HTTPException(status_code=403, detail="Permission denied")
        
    act = await Activity.get(id)
    if not act:
        raise HTTPException(status_code=404, detail="Activity not found")
        
    await act.delete()
    return {"status": "deleted"}
