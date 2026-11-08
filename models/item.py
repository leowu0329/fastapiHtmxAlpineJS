from typing import Optional
from pydantic import BaseModel

class ItemBase(BaseModel):
    name: str
    price: float
    description: Optional[str] = ""

class ItemResponse(ItemBase):
    id: int