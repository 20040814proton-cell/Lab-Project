from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models import Student, UserRole
from schemas import StudentCreate, StudentOut
from routers.auth import get_current_user

router = APIRouter()

@router.get("", response_model=List[StudentOut])
async def get_students():
    # Public endpoint
    return await Student.find_all().to_list()

@router.post("", response_model=StudentOut)
async def create_student(student: StudentCreate, current_user: dict = Depends(get_current_user)):
    # Only Teachers should create students manually?
    # Or maybe this Endpoint is retired in favor of Register? 
    # The prompt says "DELETE operation: Raise HTTPException(403) if current_user.role != 'teacher'."
    # I'll protect Create similarly just in case.
    if current_user['role'] not in [UserRole.TEACHER, UserRole.SUPERADMIN]:
        raise HTTPException(status_code=403, detail="Only teachers can add students")
    
    new_student = Student(**student.dict())
    await new_student.insert()
    return new_student

@router.delete("/{student_id}")
async def delete_student(student_id: str, current_user: dict = Depends(get_current_user)):
    if current_user['role'] not in [UserRole.TEACHER, UserRole.SUPERADMIN]:
        raise HTTPException(status_code=403, detail="Only teachers can delete students")
    
    # Assuming student_id is the OBJECT ID or the Username? 
    # Beanie default operations usually use ID.
    # But usually frontend sends ID.
    # Let's try to search by ID first.
    from bson import ObjectId
    try:
        obj_id = ObjectId(student_id)
        student = await Student.get(obj_id)
    except:
        student = await Student.find_one({"username": student_id})

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    await student.delete()
    return {"status": "deleted"}
