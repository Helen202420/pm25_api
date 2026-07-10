import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="PM2.5 精簡資料 API (自研 Box 版)")

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

CRON_SECRET = os.getenv("CRON_SECRET")

# --- 功能一：定時同步 (改為從 box 資料表撈取，格式維持不變) ---
@app.get("/api/cron/sync")
async def sync_data(key: str = Query(None)):
    # 1. 安全性檢查
    if not CRON_SECRET:
        raise HTTPException(status_code=500, detail="伺服器未設定 CRON_SECRET 環境變數")
    
    if key != CRON_SECRET:
        raise HTTPException(status_code=401, detail="驗證失敗：無效的 API Key")

    try:
        # 2. 改從自家的 box 資料表抓取特定設備 (例如 ab170023) 的最新 10 筆原始資料
        response = supabase.table("box") \
            .select("pm25, device_time") \
            .eq("device_id", "ab170011") \
            .order("device_time", desc=True) \
            .limit(10) \
            .execute()
        
        box_records = response.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"從 box 表格讀取資料出錯: {str(e)}")

    if not box_records:
        return {"status": "warning", "message": "box 表格中找不到該設備的資料"}

    # 3. 處理資料格式與時間去重：將 box 格式轉化為原本與環境署相同的規格
    to_upsert = []
    seen_times = set()  # ✨ 用來追蹤同一次批次中是否已經加入了重複的時間點

    for r in box_records:
        device_time = r.get("device_time")
        
        # 🚨 防護罩：如果時間戳記為空，或者在這一批次內已經加過相同時間的資料，就直接跳過
        if not device_time or device_time in seen_times:
            continue
            
        try:
            # 處理 PM2.5 數值轉換，若為空或無效則設為 0
            pm_val = r.get("pm25")
            val = float(pm_val) if pm_val and str(pm_val).strip() else 0
        except (ValueError, TypeError):
            val = 0
            
        to_upsert.append({
            "site": "中壢",               # 固定寫入為中壢，保持與前端 UI 一致
            "county": "桃園市",           # 固定寫入桃園市
            "pm25": val,                  # 來自盒子的 pm25 數值
            "datacreationdate": device_time,  # 盒子的時間對齊原本的時間欄位
            "itemunit": "μg/m3"           # 補上固定單位
        })
        
        # ✨ 將已處理的時間點加入集合
        seen_times.add(device_time)

    # 4. 寫入 Supabase (使用 upsert 避免重複)
    if not to_upsert:
        return {"status": "success", "synced_count": 0, "message": "本次無有效且不重複的 box 資料可同步"}

    try:
        supabase.table("pm25_data").upsert(
            to_upsert, 
            on_conflict="site,datacreationdate"
        ).execute()
        
        return {
            "status": "success", 
            "synced_count": len(to_upsert),
            "message": "中壢測站資料同步完成 (資料源：自研 Box)"
        }
    except Exception as e:
        return {"status": "error", "message": f"Supabase 寫入 pm25_data 失敗: {str(e)}"}