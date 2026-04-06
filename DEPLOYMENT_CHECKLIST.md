# 部署檢查清單

部署到 Vercel 前，請確保完成以下步驟：

## 前置準備

- [ ] 申請環境部 API Key
  - URL: https://data.moenv.gov.tw/
  - 記錄 API Key

- [ ] 建立 Supabase 專案
  - 記錄 Project URL
  - 記錄 Anon Key

- [ ] 建立 Supabase 表
  - 在 Supabase SQL 編輯器中執行 `database_setup.sql`
  - 確認表建立成功

## 本地測試

- [ ] 安裝依賴
  ```bash
  pip install -r requirements.txt
  ```

- [ ] 設置環境變數
  ```bash
  cp .env.example .env
  # 編輯 .env 填入認證資訊
  ```

- [ ] 本地運行
  ```bash
  uvicorn main:app --reload
  ```

- [ ] 運行測試
  ```bash
  python test_local.py
  ```

- [ ] 驗證 API 端點
  - 訪問 http://localhost:8000/docs 查看 Swagger UI
  - 手動測試各個端點

## 推送到 GitHub

- [ ] 初始化 git 倉庫（如未初始化）
  ```bash
  git init
  ```

- [ ] 添加所有文件
  ```bash
  git add .
  ```

- [ ] 提交變更
  ```bash
  git commit -m "Initial commit: PM2.5 API 轉接器"
  ```

- [ ] 推送到 GitHub
  ```bash
  git push origin main
  ```

## 部署到 Vercel

- [ ] 連接 GitHub
  - 登錄 Vercel: https://vercel.com
  - 連接您的 GitHub 帳戶

- [ ] 創建新專案
  - 點擊 "New Project"
  - 選擇此倉庫
  - 點擊 "Import"

- [ ] 配置項目設定
  - Framework Preset: "Other"
  - Root Directory: "./"
  - Build Command: `pip install -r requirements.txt`
  - Output Directory: (保持空白)

- [ ] 設置環境變數
  - 進入項目設定 -> Environment Variables
  - 添加以下三個變數：
    - `MOENV_API_KEY`
    - `SUPABASE_URL`
    - `SUPABASE_KEY`

- [ ] 部署
  - 點擊 "Deploy"
  - 等待部署完成

## 部署後驗證

- [ ] 測試 API 端點
  ```bash
  curl https://<your-vercel-domain>/health
  curl https://<your-vercel-domain>/api/pm25/latest
  ```

- [ ] 檢查 Cron 任務
  - 進入 Vercel 項目儀表板
  - 點擊 "Cron Jobs" 標籤
  - 確認 `/api/cron/sync` 已排程
  - 設定應為 `*/30 * * * *`

- [ ] 監控錯誤日誌
  - 進入 Vercel 項目儀表板
  - 點擊 "Functions" 標籤
  - 查看 `main` 函數的日誌
  - 確認無錯誤

- [ ] 驗證資料同步
  - 等待 cron 觸發（最多 30 分鐘）
  - 檢查 Supabase 資料庫中是否有新資料
  - 查詢 /api/pm25/latest 端點

## 常見問題

### 部署失敗
- 檢查 Vercel 構建日誌
- 確保 requirements.txt 中所有依賴都已列出
- 確保 Python 版本兼容性

### Cron 不運行
- 確認環境變數已正確設置
- 檢查 vercel.json 中的 cron schedule
- 查看 Vercel 函數日誌了解詳細信息

### 無法連接 Supabase
- 驗證 SUPABASE_URL 和 SUPABASE_KEY
- 確認 Supabase 專案未暫停
- 檢查表和 RLS 策略是否正確配置

### No data returned
- 確認 cron 任務已運行
- 檢查 Supabase 資料庫中是否有資料
- 驗證 SQL 查詢邏輯

## 後續維護

- [ ] 定期監控 API 日誌
- [ ] 監控 Supabase 資料庫使用量
- [ ] 根據需要調整 Cron 運行頻率
- [ ] 保持依賴包的更新
