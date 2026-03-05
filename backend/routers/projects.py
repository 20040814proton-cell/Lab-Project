from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models import Project, UserRole
from schemas import ProjectCreate, ProjectOut, ProjectUpdate
from routers.auth import get_current_user
from beanie import PydanticObjectId

router = APIRouter()

@router.get("/", response_model=List[ProjectOut])
async def get_projects():
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
    if current_user['role'] not in [UserRole.TEACHER, UserRole.SUPERADMIN]:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    new_project = Project(**project.dict())
    await new_project.insert()
    return new_project

@router.delete("/{id}")
async def delete_project(id: PydanticObjectId, current_user: dict = Depends(get_current_user)):
    if current_user['role'] not in [UserRole.TEACHER, UserRole.SUPERADMIN]:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    proj = await Project.get(id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    
    await proj.delete()
    return {"status": "deleted"}

@router.put("/{id}", response_model=ProjectOut)
async def update_project(id: PydanticObjectId, req: ProjectUpdate, current_user: dict = Depends(get_current_user)):
    if current_user['role'] not in [UserRole.TEACHER, UserRole.SUPERADMIN]:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    proj = await Project.get(id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Exclude unset to avoid overwriting with None
    await proj.set(req.dict(exclude_unset=True))
    return proj
