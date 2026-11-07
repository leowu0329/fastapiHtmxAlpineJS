import os
from typing import Optional
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="FastAPI + HTMX + Supabase CRUD")

# 靜態資源與模板設定
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Supabase 初始化
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-supabase-url.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "your-anon-key")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
TABLE_NAME = "products"

# -------------------------------------------------------------------
# Page & UI Endpoints
# -------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    response = supabase.table(TABLE_NAME).select("*").order("id").execute()
    # 將 request 作為第 1 個參數，context 字典作為第 2 個參數
    return templates.TemplateResponse(
        request, 
        "index.html", 
        {"items": response.data}
    )

@app.get("/items/list", response_class=HTMLResponse)
async def get_items_list(request: Request):
    response = supabase.table(TABLE_NAME).select("*").order("id").execute()
    return templates.TemplateResponse(
        request, 
        "item_table.html", 
        {"items": response.data}
    )

# -------------------------------------------------------------------
# RESTful API Endpoints (CRUD)
# -------------------------------------------------------------------

@app.post("/api/items")
async def create_item(name: str = Form(...), price: float = Form(...), description: str = Form("")):
    data = {"name": name, "price": price, "description": description}
    res = supabase.table(TABLE_NAME).insert(data).execute()
    if not res.data:
        raise HTTPException(status_code=400, detail="新增失敗")
    return HTMLResponse(status_code=200, headers={"HX-Trigger": "refreshTable"})

@app.put("/api/items/{item_id}")
async def update_item(item_id: int, name: str = Form(...), price: float = Form(...), description: str = Form("")):
    data = {"name": name, "price": price, "description": description}
    res = supabase.table(TABLE_NAME).update(data).eq("id", item_id).execute()
    if not res.data:
        raise HTTPException(status_code=400, detail="更新失敗")
    return HTMLResponse(status_code=200, headers={"HX-Trigger": "refreshTable"})

@app.delete("/api/items/{item_id}")
async def delete_item(item_id: int):
    res = supabase.table(TABLE_NAME).delete().eq("id", item_id).execute()
    if not res.data:
        raise HTTPException(status_code=400, detail="刪除失敗")
    return HTMLResponse(status_code=200, headers={"HX-Trigger": "refreshTable"})
