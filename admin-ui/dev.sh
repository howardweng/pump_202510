#!/bin/bash
# Admin UI 本地開發啟動腳本

# 如果 .env.local 不存在，從範例文件創建
if [ ! -f .env.local ]; then
    if [ -f .env.local.example ]; then
        echo "📝 創建 .env.local 文件（從範例）..."
        cp .env.local.example .env.local
        echo "✅ 請檢查並修改 .env.local 中的配置"
    else
        echo "⚠️  警告: .env.local 和 .env.local.example 都不存在"
    fi
fi

# 檢查 node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 安裝依賴..."
    npm install
fi

# 啟動開發服務器
echo "🚀 啟動 Admin UI (http://localhost:3000)..."
npm run dev

