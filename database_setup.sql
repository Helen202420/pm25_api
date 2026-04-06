-- Supabase 資料庫表建置 SQL
-- 在 Supabase SQL 編輯器中執行此指令

CREATE TABLE IF NOT EXISTS pm25_data (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  site VARCHAR(255) NOT NULL,
  county VARCHAR(100) NOT NULL,
  pm25 FLOAT8,
  datacreationdate VARCHAR(100) NOT NULL,
  itemunit VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(site, datacreationdate)
);

-- 建立索引以加快查詢
CREATE INDEX idx_pm25_site ON pm25_data(site);
CREATE INDEX idx_pm25_county ON pm25_data(county);
CREATE INDEX idx_pm25_date ON pm25_data(datacreationdate DESC);
CREATE INDEX idx_pm25_site_date ON pm25_data(site, datacreationdate DESC);

-- 啟用實時功能（選配）
ALTER TABLE pm25_data ENABLE ROW LEVEL SECURITY;

-- 建立公開讀取策略（允許所有人讀取）
CREATE POLICY "pm25_data_read_all" ON pm25_data
  FOR SELECT USING (true);

-- 建立寫入策略（需要有服務角色金鑰）
CREATE POLICY "pm25_data_write_service" ON pm25_data
  FOR INSERT WITH CHECK (true);

CREATE POLICY "pm25_data_update_service" ON pm25_data
  FOR UPDATE USING (true);
