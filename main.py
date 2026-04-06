import os
import httpx
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="PM2.5 精簡資料 API")

# 允許跨域請求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化 Supabase
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

MOENV_API_KEY = os.getenv("MOENV_API_KEY")
# 從環境變數讀取自定義的 Cron 金鑰
CRON_SECRET = os.getenv("CRON_SECRET")

# --- 功能一：定時同步 (修改後支援 Cron-job.org 驗證) ---
# 用法: /api/cron/sync?key=你的金鑰
@app.get("/api/cron/sync")
async def sync_data(key: str = Query(None)):
    # 1. 安全性檢查
    if not CRON_SECRET:
        raise HTTPException(status_code=500, detail="伺服器未設定 CRON_SECRET 環境變數")
    
    if key != CRON_SECRET:
        raise HTTPException(status_code=401, detail="驗證失敗：無效的 API Key")

    # 2. 向環境部抓取資料
    url = f"https://data.moenv.gov.tw/api/v2/aqx_p_02?api_key={MOENV_API_KEY}&format=json"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=20.0) # 設定超時防止卡死
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="環境部 API 連線失敗")
            
            data = response.json()
            records = data.get("records", [])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"抓取過程出錯: {str(e)}")

    # 3. 處理資料格式
    to_upsert = []
    for r in records:
        try:
            # 處理可能出現的空字串或無效值
            val = float(r["pm25"]) if r.get("pm25") and r["pm25"].strip() else 0
        except (ValueError, TypeError):
            val = 0
            
        to_upsert.append({
            "site": r["site"],
            "county": r["county"],
            "pm25": val,
            "datacreationdate": r["datacreationdate"],
            "itemunit": r["itemunit"]
        })

    # 4. 寫入 Supabase (使用 upsert 避免重複)
    try:
        # 確保你的 pm25_data 表格有設定 site 和 datacreationdate 的唯一約束 (Unique Constraint)
        supabase.table("pm25_data").upsert(
            to_upsert, 
            on_conflict="site,datacreationdate"
        ).execute()
        
        return {
            "status": "success", 
            "synced_count": len(to_upsert),
            "message": "資料同步完成"
        }
    except Exception as e:
        return {"status": "error", "message": f"Supabase 寫入失敗: {str(e)}"}


# --- 功能二：獲取「最新一筆」資料 ---
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
@app.get("/api/pm25/history")
def get_history(site: str):
    if not site:
        raise HTTPException(status_code=400, detail="必須提供測站名稱(site)")
        
    try:
        result = supabase.table("pm25_data") \
            .select("*") \
            .eq("site", site) \
            .order("datacreationdate", desc=True) \
            .limit(24) \
            .execute()
            
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))