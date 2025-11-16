-- PostgreSQL 初始化腳本
-- Pump Testing Platform Database Schema

-- 創建擴展（如果需要）
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 測試數據表（範例）
-- 實際的資料表結構將在後端應用中定義

-- 創建測試連接表（用於驗證資料庫連接）
CREATE TABLE IF NOT EXISTS health_check (
    id SERIAL PRIMARY KEY,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'OK'
);

-- 插入初始健康檢查記錄
INSERT INTO health_check (status) VALUES ('Database initialized successfully');

-- 顯示資料庫版本
SELECT version();



