import os
import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="PM2.5 精簡資料 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

MOENV_API_KEY = os.getenv("MOENV_API_KEY")

# --- 功能一：定時同步 (保持不變) ---
@app.get("/api/cron/sync")
async def sync_data():
    url = f"https://data.moenv.gov.tw/api/v2/aqx_p_02?api_key={MOENV_API_KEY}&format=json"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="環境部 API 連線失敗")
        records = response.json().get("records", [])

    to_upsert = []
    for r in records:
        try:
            val = float(r["pm25"]) if r["pm25"] and r["pm25"].strip() else 0
        except:
            val = 0
        to_upsert.append({
            "site": r["site"],
            "county": r["county"],
            "pm25": val,
            "datacreationdate": r["datacreationdate"],
            "itemunit": r["itemunit"]
        })

    try:
        supabase.table("pm25_data").upsert(to_upsert, on_conflict="site,datacreationdate").execute()
        return {"status": "success", "synced_count": len(to_upsert)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# --- 功能二：獲取「最新一筆」資料 ---
# 支援兩種用法：
# 1. 不傳參數：抓全台灣最新的一筆 (最新的那個測站)
# 2. 傳 site: 抓指定測站最新一筆
@app.get("/api/pm25/latest")
def get_latest(site: str = None):
    try:
        query = supabase.table("pm25_data").select("*").order("datacreationdate", desc=True)
        
        if site:
            query = query.eq("site", site)
            
        result = query.limit(1).execute()
        
        if not result.data:
            return {"status": "error", "message": "查無資料"}
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- 功能三：獲取指定測站「最近 24 筆」歷史資料 ---
# 用法: /api/pm25/history?site=板橋
@app.get("/api/pm25/history")
def get_history(site: str):
    if not site:
        return {"status": "error", "message": "必須提供測站名稱(site)"}
        
    try:
        result = supabase.table("pm25_data") \
            .select("*") \
            .eq("site", site) \
            .order("datacreationdate", desc=True) \
            .limit(24) \
            .execute()
            
        return result.data  # 回傳 24 筆資料的陣列
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))