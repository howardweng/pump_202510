#!/bin/bash
# Admin API 本地開發啟動腳本

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

# 檢查 Python 虛擬環境
if [ ! -d "venv" ]; then
    echo "📦 創建 Python 虛擬環境..."
    python3 -m venv venv
fi

# 啟動虛擬環境
source venv/bin/activate

# 安裝依賴
echo "📥 安裝依賴..."
pip install -q -r requirements.txt

# 啟動 API（帶熱重載）
echo "🚀 啟動 Admin API (http://localhost:8001)..."
echo "📚 API 文檔: http://localhost:8001/docs"
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

