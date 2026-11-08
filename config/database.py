import os
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("請先設定 SUPABASE_URL 與 SUPABASE_KEY 環境變數")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
TABLE_NAME = "products"
