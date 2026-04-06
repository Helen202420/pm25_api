"""
本地測試腳本 - 不需要 Vercel 或完整的 Supabase 連接
用於測試 API 邏輯
"""

import os
import sys
import requests
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 本地 API 基礎 URL
BASE_URL = "http://localhost:8000"

def test_health():
    """測試健康檢查"""
    print("\n=== 測試健康檢查 ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"狀態碼: {response.status_code}")
    print(f"回應: {response.json()}")
    assert response.status_code == 200

def test_root():
    """測試根路徑"""
    print("\n=== 測試根路徑 ===")
    response = requests.get(BASE_URL)
    print(f"狀態碼: {response.status_code}")
    print(f"回應: {response.json()}")
    assert response.status_code == 200

def test_sync():
    """測試同步端點"""
    print("\n=== 測試同步資料 ===")
    print("提示: 確保設置了 MOENV_API_KEY 和 Supabase 認證")
    response = requests.get(f"{BASE_URL}/api/cron/sync")
    print(f"狀態碼: {response.status_code}")
    print(f"回應: {response.json()}")
    # 可能是 success、warning 或 error
    assert response.status_code == 200

def test_latest():
    """測試獲取最新資料"""
    print("\n=== 測試獲取最新資料 ===")
    print("提示: 確保資料庫中已有資料")
    
    # 不篩選縣市
    response = requests.get(f"{BASE_URL}/api/pm25/latest")
    print(f"狀態碼: {response.status_code}")
    print(f"返回筆數: {len(response.json())}")
    if response.json():
        print(f"第一筆資料: {response.json()[0]}")
    assert response.status_code == 200
    
    # 篩選特定縣市（示例）
    print("\n--- 篩選縣市 (台北市) ---")
    response = requests.get(f"{BASE_URL}/api/pm25/latest?county=台北市")
    print(f"狀態碼: {response.status_code}")
    print(f"返回筆數: {len(response.json())}")
    assert response.status_code == 200

def main():
    print("PM2.5 API 轉接器 - 本地測試套件")
    print(f"目標 API: {BASE_URL}")
    print("\n請確保已執行: uvicorn main:app --reload")
    
    try:
        # 測試連接
        print("\n正在連接到本地 API...")
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print("✓ 連接成功")
    except Exception as e:
        print(f"✗ 連接失敗: {e}")
        print("請先啟動應用: uvicorn main:app --reload")
        sys.exit(1)
    
    try:
        test_health()
        test_root()
        
        # 根據是否配置了認證，決定是否運行需要資料庫的測試
        moenv_key = os.getenv("MOENV_API_KEY")
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if moenv_key and supabase_url and supabase_key:
            test_sync()
            test_latest()
        else:
            print("\n⚠️  跳過需要認證的測試 (未配置 MOENV_API_KEY 或 Supabase 認證)")
            print("   請複製 .env.example 為 .env 並填入認證資訊")
        
        print("\n✓ 所有測試通過！")
    
    except AssertionError as e:
        print(f"\n✗ 測試失敗: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 發生錯誤: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
