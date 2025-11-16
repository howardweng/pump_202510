#!/bin/bash
# 一鍵啟動本地開發環境

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 啟動模擬器 Admin 本地開發環境"
echo "=================================="

# 1. 啟動基礎設施（Docker）
echo ""
echo "📦 步驟 1/3: 啟動基礎設施服務（Docker）..."
docker compose up -d mqtt-broker postgres modbus-simulator

# 等待服務就緒
echo "⏳ 等待服務啟動..."
sleep 3

# 檢查服務狀態
echo ""
echo "📊 服務狀態："
docker compose ps mqtt-broker postgres modbus-simulator

# 2. 啟動 Admin API
echo ""
echo "🔧 步驟 2/3: 啟動 Admin API..."
cd admin-api
if [ ! -f .env.local ]; then
    if [ -f .env.local.example ]; then
        cp .env.local.example .env.local
        echo "✅ 已創建 .env.local 文件"
    fi
fi

# 在後台啟動 API
echo "🚀 啟動 Admin API (http://localhost:8001)..."
chmod +x dev.sh
./dev.sh > /tmp/admin-api.log 2>&1 &
API_PID=$!
echo "   PID: $API_PID"
echo "   日誌: tail -f /tmp/admin-api.log"

# 3. 啟動 Admin UI
echo ""
echo "🎨 步驟 3/3: 啟動 Admin UI..."
cd ../admin-ui
if [ ! -f .env.local ]; then
    if [ -f .env.local.example ]; then
        cp .env.local.example .env.local
        echo "✅ 已創建 .env.local 文件"
    fi
fi

# 在後台啟動 UI
echo "🚀 啟動 Admin UI (http://localhost:3000)..."
chmod +x dev.sh
./dev.sh > /tmp/admin-ui.log 2>&1 &
UI_PID=$!
echo "   PID: $UI_PID"
echo "   日誌: tail -f /tmp/admin-ui.log"

# 等待一下讓服務啟動
sleep 5

echo ""
echo "=================================="
echo "✅ 開發環境已啟動！"
echo ""
echo "📍 訪問地址："
echo "   - Admin UI:  http://localhost:3000"
echo "   - Admin API: http://localhost:8001"
echo "   - API 文檔:  http://localhost:8001/docs"
echo ""
echo "📝 查看日誌："
echo "   - Admin API: tail -f /tmp/admin-api.log"
echo "   - Admin UI:  tail -f /tmp/admin-ui.log"
echo ""
echo "🛑 停止服務："
echo "   - 按 Ctrl+C 停止此腳本"
echo "   - 或運行: ./stop-dev.sh"
echo ""
echo "💡 提示：服務在後台運行，可以關閉此終端"
echo ""

# 保存 PID 到文件
echo "$API_PID" > /tmp/admin-api.pid
echo "$UI_PID" > /tmp/admin-ui.pid

# 等待用戶中斷
trap "echo ''; echo '🛑 正在停止服務...'; kill $API_PID $UI_PID 2>/dev/null; exit" INT TERM
wait

