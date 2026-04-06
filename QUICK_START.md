# 部署流程快速指南

## 環境準備

### 1. 註冊必要的服務帳號

#### 環保部 API
- 訪問 https://data.moenv.gov.tw/
- 申請 PM2.5 (AQX_P_02) API 授權碼

#### Supabase
- 訪問 https://supabase.com 創建帳號
- 新建一個專案
- 記錄下 Project URL 和 Service Role Key（**不是 Anon Key**）

#### GitHub
- 準備一個 GitHub 帳號（用於推送代碼到 Vercel）

#### Vercel
- 訪問 https://vercel.com 並使用 GitHub 帳戶登錄

## 本地開發

```bash
# 1. 安裝依賴
pip install -r requirements.txt

# 2. 複製環境變數模板
cp .env.example .env

# 3. 編輯 .env 文件，填入三個認證資訊：
#    - MOENV_API_KEY
#    - SUPABASE_URL
#    - SUPABASE_KEY (Service Role Key)

# 4. 啟動本地伺服器
uvicorn main:app --reload

# 5. 訪問 http://localhost:8000/docs 測試 API
```

## Supabase 資料庫設置

1. 登錄 Supabase 後台
2. 進入 "SQL Editor"
3. 複製 `database_setup.sql` 的全部內容並執行
4. 等待表建立完成

## GitHub 推送

```bash
git init
git add .
git commit -m "Initial commit: PM2.5 API"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/pm25.git
git push -u origin main
```

## Vercel 部署

### Step 1: 導入專案
1. 登錄 Vercel (https://vercel.com)
2. 點擊 "Add New" → "Project"
3. 選擇 "Import Git Repository"
4. 選擇您的 pm25 倉庫

### Step 2: 配置環境變數
在 Vercel 中設置以下環境變數：
- `MOENV_API_KEY`: 您的環保部 API 密鑰
- `SUPABASE_URL`: 您的 Supabase Project URL
- `SUPABASE_KEY`: 您的 Supabase Service Role Key

### Step 3: 部署
點擊 "Deploy" 按鈕

## 驗證部署

### 1. 測試 API 端點
```bash
# 替換 <your-deployment-url> 為您的 Vercel 部署 URL

# 健康檢查
curl https://<your-deployment-url>/health

# 手動觸發同步
curl https://<your-deployment-url>/api/cron/sync

# 查詢資料
curl https://<your-deployment-url>/api/pm25

# 篩選特定縣市
curl "https://<your-deployment-url>/api/pm25?county=台北市"
```

### 2. 檢查 Cron 排程
- 進入 Vercel 項目儀表板
- 點擊 "Cron Jobs" 標籤
- 確認 `/api/cron/sync` 已排程，scheduled 為 `*/30 * * * *`

### 3. 驗證資料同步
- 等待 30 分鐘或手動觸發 `/api/cron/sync`
- 檢查 Supabase 資料庫中是否有新資料

## 常見問題

### "連線環境部失敗"
- 確保 MOENV_API_KEY 正確
- 檢查環保部 API 服務狀況

### "Supabase 連接失敗"
- 確保 SUPABASE_URL 和 SUPABASE_KEY 正確
- 確認使用的是 **Service Role Key** 而不是 Anon Key
- 檢查表是否已創建

### Cron 任務未運行
- 查看 Vercel 函數日誌
- 確認 vercel.json 配置正確
- 檢查環境變數是否設置

## API 使用示例

### 獲取最新資料（限 100 筆）
```bash
curl https://<your-deployment-url>/api/pm25
```

### 篩選特定縣市
```bash
curl "https://<your-deployment-url>/api/pm25?county=台北市"
```

### 響應格式
```json
[
  {
    "id": 1,
    "site": "北投",
    "county": "台北市",
    "pm25": 28.5,
    "datacreationdate": "2024-01-15 10:00:00",
    "itemunit": "μg/m³"
  }
]
```

## 後續調整

### 修改 Cron 運行頻率
編輯 `vercel.json`：
```json
{
  "crons": [
    {
      "path": "/api/cron/sync",
      "schedule": "*/15 * * * *"  // 改為每 15 分鐘
    }
  ]
}
```

然後推送到 GitHub，Vercel 會自動重新部署。

### 擴展 API
編輯 `main.py` 添加新的端點，推送後 Vercel 會自動更新。
