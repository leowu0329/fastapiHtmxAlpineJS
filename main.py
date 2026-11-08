from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers.items import router as items_router

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="FastAPI + HTMX + Supabase Modular CRUD")

# 靜態資源掛載
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# 註冊路由
app.include_router(items_router)