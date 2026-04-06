import os
import httpx
from fastapi import FastAPI, HTTPException, Query
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
CRON_SECRET = os.getenv("CRON_SECRET")

# --- 功能一：定時同步 (僅篩選 桃園市-中壢 測站資料) ---
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
            response = await client.get(url, timeout=30.0)
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail=f"環境部 API 連線失敗: {response.status_code}")
            
            # 取得原始資料
            raw_data = response.json()
            
            # --- 重點修正：判斷回傳格式 ---
            # 如果 raw_data 本身就是 list，直接使用；如果是 dict，嘗試抓取 'records'
            if isinstance(raw_data, list):
                records = raw_data
            elif isinstance(raw_data, dict):
                records = raw_data.get("records", [])
            else:
                records = []
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"抓取過程出錯: {str(e)}")

    if not records:
        return {"status": "warning", "message": "未抓取到任何資料記錄"}

    # 3. 處理資料格式與「桃園市-中壢站」篩選
    to_upsert = []
    for r in records:
        # --- 核心修改：精確篩選縣市為「桃園市」且測站為「中壢」 ---
        if r.get("county") == "桃園市" and r.get("site") == "中壢":
            try:
                # 處理 PM2.5 數值轉換，若為空字串或無效值則設為 0
                pm_val = r.get("pm25")
                val = float(pm_val) if pm_val and str(pm_val).strip() else 0
            except (ValueError, TypeError):
                val = 0
                
            to_upsert.append({
                "site": r.get("site"),
                "county": r.get("county"),
                "pm25": val,
                "datacreationdate": r.get("datacreationdate"),
                "itemunit": r.get("itemunit")
            })

    # 4. 寫入 Supabase (使用 upsert 避免重複)
    if not to_upsert:
        return {"status": "success", "synced_count": 0, "message": "本次抓取無桃園市中壢測站資料"}

    try:
        supabase.table("pm25_data").upsert(
            to_upsert, 
            on_conflict="site,datacreationdate"
        ).execute()
        
        return {
            "status": "success", 
            "synced_count": len(to_upsert),
            "message": "中壢測站資料同步完成"
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