from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from config.database import supabase, TABLE_NAME

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter()

# -------------------------------------------------------------------
# Page & UI Endpoints
# -------------------------------------------------------------------

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    response = supabase.table(TABLE_NAME).select("*").order("id").execute()
    return templates.TemplateResponse(
        request, 
        "index.html", 
        {"items": response.data}
    )

@router.get("/items/list", response_class=HTMLResponse)
async def get_items_list(request: Request):
    """HTMX 局部刷新：僅回傳表格組件"""
    response = supabase.table(TABLE_NAME).select("*").order("id").execute()
    return templates.TemplateResponse(
        request, 
        "components/item_table.html", 
        {"items": response.data}
    )

# -------------------------------------------------------------------
# RESTful API Endpoints (CRUD)
# -------------------------------------------------------------------

@router.post("/api/items")
async def create_item(name: str = Form(...), price: float = Form(...), description: str = Form("")):
    data = {"name": name, "price": price, "description": description}
    res = supabase.table(TABLE_NAME).insert(data).execute()
    if not res.data:
        raise HTTPException(status_code=400, detail="新增失敗")
    return HTMLResponse(status_code=200, headers={"HX-Trigger": "refreshTable"})

@router.put("/api/items/{item_id}")
async def update_item(item_id: int, name: str = Form(...), price: float = Form(...), description: str = Form("")):
    data = {"name": name, "price": price, "description": description}
    res = supabase.table(TABLE_NAME).update(data).eq("id", item_id).execute()
    if not res.data:
        raise HTTPException(status_code=400, detail="更新失敗")
    return HTMLResponse(status_code=200, headers={"HX-Trigger": "refreshTable"})

@router.delete("/api/items/{item_id}")
async def delete_item(item_id: int):
    res = supabase.table(TABLE_NAME).delete().eq("id", item_id).execute()
    if not res.data:
        raise HTTPException(status_code=400, detail="刪除失敗")
    return HTMLResponse(status_code=200, headers={"HX-Trigger": "refreshTable"})