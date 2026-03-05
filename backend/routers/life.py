from fastapi import APIRouter
from typing import List
from models import LifeItem
from schemas import LifeItemCreate, LifeItemOut

router = APIRouter()

@router.get("/", response_model=List[LifeItemOut])
async def get_life_items():
    return await LifeItem.find_all().sort("-date").to_list()

@router.post("/", response_model=LifeItemOut)
async def create_life_item(item: LifeItemCreate):
    new_item = LifeItem(**item.dict())
    await new_item.insert()
    return new_item
