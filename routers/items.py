from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from config.database import supabase, TABLE_NAME, CATEGORY_TABLE_NAME

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter()

# -------------------------------------------------------------------
# Page & UI Endpoints
# -------------------------------------------------------------------

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    products_res = supabase.table(TABLE_NAME).select("*").order("id").execute()
    categories_res = supabase.table(CATEGORY_TABLE_NAME).select("*").order("id").execute()
    return templates.TemplateResponse(
        request, 
        "index.html", 
        {"items": products_res.data, "categories": categories_res.data}
    )

@router.get("/items/list", response_class=HTMLResponse)
async def get_items_list(request: Request):
    products_res = supabase.table(TABLE_NAME).select("*").order("id").execute()
    return templates.TemplateResponse(
        request, 
        "components/item_table.html", 
        {"items": products_res.data}
    )

@router.get("/categories/options", response_class=HTMLResponse)
async def get_categories_options(request: Request):
    """HTMX 刷新：回傳最新的分類下拉選單與列表組件"""
    categories_res = supabase.table(CATEGORY_TABLE_NAME).select("*").order("id").execute()
    return templates.TemplateResponse(
        request, 
        "components/category_list.html", 
        {"categories": categories_res.data}
    )

# -------------------------------------------------------------------
# Product CRUD
# -------------------------------------------------------------------

@router.post("/api/items")
async def create_item(name: str = Form(...), price: float = Form(...), category: str = Form("雜項"), description: str = Form("")):
    data = {"name": name, "price": price, "category": category, "description": description}
    res = supabase.table(TABLE_NAME).insert(data).execute()
    if not res.data:
        raise HTTPException(status_code=400, detail="新增失敗")
    return HTMLResponse(status_code=200, headers={"HX-Trigger": "refreshTable"})

@router.put("/api/items/{item_id}")
async def update_item(item_id: int, name: str = Form(...), price: float = Form(...), category: str = Form("雜項"), description: str = Form("")):
    data = {"name": name, "price": price, "category": category, "description": description}
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

# -------------------------------------------------------------------
# Category CRUD (分類管理 API)
# -------------------------------------------------------------------

@router.post("/api/categories")
async def create_category(name: str = Form(...)):
    res = supabase.table(CATEGORY_TABLE_NAME).insert({"name": name}).execute()
    if not res.data:
        raise HTTPException(status_code=400, detail="新增分類失敗")
    return HTMLResponse(status_code=200, headers={"HX-Trigger": "refreshCategories"})

@router.delete("/api/categories/{cat_id}")
async def delete_category(cat_id: int):
    res = supabase.table(CATEGORY_TABLE_NAME).delete().eq("id", cat_id).execute()
    if not res.data:
        raise HTTPException(status_code=400, detail="刪除分類失敗")
    return HTMLResponse(status_code=200, headers={"HX-Trigger": "refreshCategories"})
