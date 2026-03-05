from fastapi import APIRouter
from typing import List
from models import ShowcaseItem
from schemas import ShowcaseItemCreate, ShowcaseItemOut

router = APIRouter()

@router.get("/", response_model=List[ShowcaseItemOut])
async def get_showcase_items():
    return await ShowcaseItem.find_all().sort("-date").to_list()

@router.post("/", response_model=ShowcaseItemOut)
async def create_showcase_item(item: ShowcaseItemCreate):
    new_item = ShowcaseItem(**item.dict())
    await new_item.insert()
    return new_item
