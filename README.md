# PM2.5 API 轉接器

這是一個從環境部開放資料平台抓取 PM2.5 資料，存入 Supabase，並提供 API 的 FastAPI 應用。

## 功能

- **自動同步**: 每 30 分鐘從環境部 API 抓取最新 PM2.5 資料
- **資料存儲**: 使用 Supabase 存儲資料，避免重複寫入
- **資料查詢**: 提供 REST API 查詢最新資料，支援按縣市篩選

## 技術棧

- **框架**: FastAPI
- **資料庫**: Supabase (PostgreSQL)
- **部署**: Vercel
- **排程**: Vercel Cron Functions

## 快速開始

### 1. 克隆並設置該項目

```bash
git clone <your-repo>
cd pm25
pip install -r requirements.txt
```

### 2. 設置環境變數

複製 `.env.example` 為 `.env` 並填入認證資訊：

```bash
cp .env.example .env
```

編輯 `.env` 檔案：
- **MOENV_API_KEY**: 從 https://data.moenv.gov.tw/ 申請
- **SUPABASE_URL**: 您的 Supabase 專案 URL
- **SUPABASE_KEY**: 您的 Supabase **Service Role Key**（注意：必須是 Service Role Key，不是 Anon Key）

### 3. 設置 Supabase 資料庫

在 Supabase SQL 編輯器中執行 `database_setup.sql` 中的指令以建立表和索引。

### 4. 本地開發

```bash
uvicorn main:app --reload
```

應用將在 `http://localhost:8000` 運行。

訪問 `http://localhost:8000/docs` 查看 Swagger API 文檔。

## API 端點

### 1. 健康檢查

```
GET /health
```

### 2. 同步資料 (Cron 觸發)

```
GET /api/cron/sync
```

供 Vercel Cron 每 30 分鐘觸發一次。返回同步結果。

**回應例子**:
```json
{
  "status": "success",
  "synced_count": 75,
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

### 3. 獲取最新資料

```
GET /api/pm25?county=台北市
```

**參數**:
- `county` (可選): 篩選特定縣市

**回應例子**:
```json
[
  {
    "id": 1,
    "site": "北投",
    "county": "台北市",
    "pm25": 28.5,
    "datacreationdate": "2024-01-15 10:00:00",
    "itemunit": "μg/m³"
  },
  {
    "id": 2,
    "site": "中山",
    "county": "台北市",
    "pm25": 32.1,
    "datacreationdate": "2024-01-15 10:00:00",
    "itemunit": "μg/m³"
  }
]
```

## 部署到 Vercel

### 1. 連接 GitHub

將此專案推送到 GitHub。

### 2. 在 Vercel 創建新專案

- 連接您的 GitHub 帳戶
- 選擇此倉庫
- Vercel 將自動偵測 FastAPI 應用

### 3. 設置環境變數

在 Vercel 專案設定中添加：
- `MOENV_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`

### 4. 部署

點擊部署按鈕。

### 5. 驗證 Cron 是否運行

在 Vercel 儀表板的 "Cron Jobs" 標籤中查看排程任務的運行日誌。

## Supabase 表結構

```sql
pm25_data 表包含以下欄位：
- id: 主鍵
- site: 測站名稱
- county: 縣市名稱
- pm25: PM2.5 濃度值
- datacreationdate: 資料建置日期
- itemunit: 測項單位
- created_at: 記錄建立時間
- updated_at: 記錄更新時間

唯一鍵: (site, datacreationdate)
```

## 故障排除

### API 無法連接

1. 確保 `MOENV_API_KEY` 正確
2. 檢查網路連接
3. 查看 Vercel 函數日誌

### Supabase 連接失敗

1. 確保 `SUPABASE_URL` 和 `SUPABASE_KEY` 正確
2. 檢查 Supabase 服務状況
3. 確保表已正確建立

### 資料未更新

1. 檢查 Vercel Cron Jobs 日誌
2. 確保 `/api/cron/sync` 端點返回成功狀態
3. 檢查 Supabase 是否有錯誤日誌

## 授權

本專案使用 MIT 授權。

## 環境部開放資料

- 資料集代碼: AQX_P_02
- API URL: https://data.moenv.gov.tw/api/v2/aqx_p_02
- 申請 API Key: https://data.moenv.gov.tw/
