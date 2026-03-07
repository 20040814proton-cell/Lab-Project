from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from models import Project, UserRole
from schemas import ProjectCreate, ProjectOut, ProjectUpdate
from routers.auth import get_current_user
from beanie import PydanticObjectId

router = APIRouter()

def is_manager(current_user: dict) -> bool:
    return current_user.get("role") in [UserRole.TEACHER, UserRole.SUPERADMIN]

def is_owner(current_user: dict, project: Project) -> bool:
    owner_id = getattr(project, "created_by_id", None)
    return bool(owner_id) and str(owner_id) == str(current_user.get("id"))

def can_manage(current_user: dict, project: Project) -> bool:
    return is_manager(current_user) or is_owner(current_user, project)

@router.get("/", response_model=List[ProjectOut])
async def get_projects(creator: Optional[str] = Query(None)):
    if creator:
        return await Project.find({"created_by_username": creator}).sort("-created_at").to_list()
    return await Project.find_all().sort("-created_at").to_list()

@router.get("/stats")
async def get_stats():
    ongoing = await Project.find({"status": "进行中"}).count()
    completed = await Project.find({"status": "已结题"}).count()
    total = await Project.find_all().count()
    
    return {
        "ongoing": ongoing,
        "completed": completed,
        "total": total
    }

@router.post("/", response_model=ProjectOut)
async def create_project(project: ProjectCreate, current_user: dict = Depends(get_current_user)):
    new_project = Project(
        **project.dict(),
        created_by_id=str(current_user["id"]),
        created_by_username=current_user.get("username"),
    )
    await new_project.insert()
    return new_project

@router.delete("/{id}")
async def delete_project(id: PydanticObjectId, current_user: dict = Depends(get_current_user)):
    proj = await Project.get(id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    if not can_manage(current_user, proj):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    await proj.delete()
    return {"status": "deleted"}

@router.put("/{id}", response_model=ProjectOut)
async def update_project(id: PydanticObjectId, req: ProjectUpdate, current_user: dict = Depends(get_current_user)):
    proj = await Project.get(id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    if not can_manage(current_user, proj):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    # Exclude unset to avoid overwriting with None
    await proj.set(req.dict(exclude_unset=True))
    return proj
