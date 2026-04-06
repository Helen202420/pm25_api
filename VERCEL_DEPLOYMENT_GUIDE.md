# Vercel 部署指南 - PM2.5 API 轉接器

## 部署前準備

### 1. 確保本地測試通過

```bash
# 安裝依賴
pip install -r requirements.txt

# 設置環境變數
cp .env.example .env
# 編輯 .env，填入：
# - MOENV_API_KEY
# - SUPABASE_URL
# - SUPABASE_KEY

# 運行本地應用
uvicorn main:app --reload

# 在另一個終端運行測試
python test_local.py
```

### 2. 準備 Git 倉庫

```bash
# 初始化 Git（如果還沒有）
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: PM2.5 API"

# 推送到 GitHub（假設已連接遠端倉庫）
git push origin main
```

## Vercel 部署步驟

### Step 1: 登錄 Vercel

訪問 https://vercel.com 並使用 GitHub 帳戶登錄。

### Step 2: 導入項目

1. 點擊 "Add New..." → "Project"
2. 選擇 "Import Git Repository"
3. 搜索並選擇您的 PM2.5 倉庫
4. 點擊 "Import"

### Step 3: 配置項目

在 "Configure Project" 頁面：

- **Project Name**: 輸入項目名稱（如 `pm25-api`）
- **Framework**: 選擇 "Other"
- **Root Directory**: 保持 "./"
- **Build Command**: 保持空白或輸入 `pip install -r requirements.txt`
- **Output Directory**: 保持空白

### Step 4: 環境變數配置

在 "Environment Variables" 部分，點擊 "Add New" 為以下變數添加值：

```
Name: MOENV_API_KEY
Value: <your_moenv_api_key>

Name: SUPABASE_URL
Value: https://your-project.supabase.co

Name: SUPABASE_KEY
Value: <your_supabase_anon_key>
```

**注意**: 這些變數應該在部署時設置，不應提交到版本控制。

### Step 5: 部署

1. 檢查所有設置無誤
2. 點擊 "Deploy"
3. 等待部署完成（通常 2-3 分鐘）

## 部署後配置

### 檢查 Cron 任務

部署成功後：

1. 進入您的項目儀表板
2. 點擊 "Cron Jobs" 標籤
3. 您應該看到：
   - **Path**: `/api/cron/sync`
   - **Schedule**: `*/30 * * * *`（每 30 分鐘運行一次）

### 驗證 API 端點

使用 curl 或 Postman 測試部署的 API：

```bash
# 替換 <your-deployment-url> 為您的 Vercel 部署 URL
# 例如: pm25-api.vercel.app

# 健康檢查
curl https://<your-deployment-url>/health

# 獲取最新資料
curl https://<your-deployment-url>/api/pm25/latest

# 獲取特定縣市資料
curl "https://<your-deployment-url>/api/pm25/latest?county=台北市"

# 查看 API 文檔
# 訪問 https://<your-deployment-url>/docs
```

## 監控和管理

### 查看函數日誌

1. 項目儀表板 → "Functions" 標籤
2. 點擊 `main` 函數
3. 查看最近的調用日誌和錯誤

### 查看 Cron Jobs 日誌

1. 項目儀表板 → "Cron Jobs" 標籤
2. 查看 `/api/cron/sync` 的運行歷史
3. 點擊特定的運行查看詳細日誌

### 監控費用

Vercel 提供免費層級，包括：
- 無限制的無伺服器函數執行
- 每月有一定的執行時間和頻帶限制（通常足夠）

如需更多資源，可升級至付費計畫。

## 常見部署問題

### 問題 1: "Module not found" 錯誤

**解決方案**:
- 確保所有依賴都在 requirements.txt 中
- 檢查 Python 版本兼容性
- 在 Vercel 構建日誌中查看錯誤詳情

### 問題 2: Cron 任務未運行

**排查步驟**:
1. 檢查 vercel.json 中的 cron 配置是否正確
2. 查看 Vercel 儀表板的 Cron Jobs 日誌
3. 驗證 `/api/cron/sync` 端點是否可訪問
4. 檢查環境變數是否正確設置

### 問題 3: Supabase 連接失敗

**排查步驟**:
1. 驗證 SUPABASE_URL 和 SUPABASE_KEY 是否正確
2. 檢查 Supabase 專案是否已啟用
3. 確認表已正確建立（檢查 Supabase 儀表板）
4. 查看 Vercel 函數日誌中的錯誤信息

### 問題 4: 環保部 API 無法連接

**排查步驟**:
1. 驗證 MOENV_API_KEY 是否有效
2. 測試 cron 端點：`/api/cron/sync`
3. 檢查環保部 API 服務是否可用
4. 查看 Vercel 函數日誌中的 HTTP 錯誤代碼

## 自動部署

### 啟用自動部署

1. 項目設定 → "Git" 標籤
2. "Production Branch" 設置為 `main`（或您的主分支）
3. 每次推送到主分支時，Vercel 將自動部署

### 禁用自動部署

1. 項目設定 → "Git" 標籤
2. 將 "Auto-deploy" 關閉
3. 手動部署：進入儀表板點擊 "Redeploy"

## 自定義域名

1. 項目設定 → "Domains" 標籤
2. 點擊 "Add" 添加自定義域名
3. 按照指示配置 DNS 記錄
4. 等待 DNS 生效

## 性能優化

### 冷啟動最小化

- 確保 requirements.txt 只包含必要的依賴
- 考慮使用更輕量級的依賴（如 FastAPI 替代 Flask）

### Cron 間隔調整

如果需要更頻繁的更新，編輯 vercel.json：

```json
"crons": [
  {
    "path": "/api/cron/sync",
    "schedule": "*/15 * * * *"  // 改為每 15 分鐘
  }
]
```

**注意**: 更頻繁的 cron 可能增加成本。

## 回滾部署

如需回滾到之前的部署：

1. 項目儀表板 → "Deployments" 標籤
2. 找到想要回滾到的部署
3. 點擊三個點菜單 → "Promote to Production"

## 後續維護

1. **定期檢查日誌**：每週查看 Cron Jobs 和 Functions 日誌
2. **監控費用**：檢查每月的使用情況和成本
3. **更新依賴**：定期檢查和更新 requirements.txt 中的包
4. **備份資料**：定期備份 Supabase 中的資料

## 支持和幫助

- Vercel 文檔: https://vercel.com/docs
- FastAPI 文檔: https://fastapi.tiangolo.com
- Supabase 文檔: https://supabase.com/docs
- 環保部開放資料: https://data.moenv.gov.tw
