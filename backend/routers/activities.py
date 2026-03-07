from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from models import Activity, UserRole
from schemas import ActivityCreate, ActivityOut, ActivityUpdate
from routers.auth import get_current_user
from beanie import PydanticObjectId

router = APIRouter()

def is_manager(current_user: dict) -> bool:
    return current_user.get("role") in [UserRole.TEACHER, UserRole.SUPERADMIN]

def is_owner(current_user: dict, activity: Activity) -> bool:
    owner_id = getattr(activity, "created_by_id", None)
    return bool(owner_id) and str(owner_id) == str(current_user.get("id"))

def can_manage(current_user: dict, activity: Activity) -> bool:
    return is_manager(current_user) or is_owner(current_user, activity)

@router.get("/", response_model=List[ActivityOut])
async def get_activities(creator: Optional[str] = Query(None)):
    if creator:
        return await Activity.find({"created_by_username": creator}).sort("-date").to_list()
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
    new_activity = Activity(
        **activity.dict(),
        created_by_id=str(current_user["id"]),
        created_by_username=current_user.get("username"),
    )
    await new_activity.insert()
    return new_activity

@router.put("/{id}", response_model=ActivityOut)
async def update_activity(id: PydanticObjectId, req: ActivityUpdate, current_user: dict = Depends(get_current_user)):
    act = await Activity.get(id)
    if not act:
        raise HTTPException(status_code=404, detail="Activity not found")

    if not can_manage(current_user, act):
        raise HTTPException(status_code=403, detail="Permission denied")
        
    await act.set(req.dict(exclude_unset=True))
    return act

@router.delete("/{id}")
async def delete_activity(id: PydanticObjectId, current_user: dict = Depends(get_current_user)):
    act = await Activity.get(id)
    if not act:
        raise HTTPException(status_code=404, detail="Activity not found")

    if not can_manage(current_user, act):
        raise HTTPException(status_code=403, detail="Permission denied")
        
    await act.delete()
    return {"status": "deleted"}
