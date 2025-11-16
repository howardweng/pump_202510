#!/bin/bash
# 停止本地開發環境

echo "🛑 停止本地開發環境..."

# 停止 Admin API
if [ -f /tmp/admin-api.pid ]; then
    API_PID=$(cat /tmp/admin-api.pid)
    if ps -p $API_PID > /dev/null 2>&1; then
        echo "   停止 Admin API (PID: $API_PID)..."
        kill $API_PID 2>/dev/null
        rm /tmp/admin-api.pid
    fi
fi

# 停止 Admin UI
if [ -f /tmp/admin-ui.pid ]; then
    UI_PID=$(cat /tmp/admin-ui.pid)
    if ps -p $UI_PID > /dev/null 2>&1; then
        echo "   停止 Admin UI (PID: $UI_PID)..."
        kill $UI_PID 2>/dev/null
        rm /tmp/admin-ui.pid
    fi
fi

# 可選：停止 Docker 服務
read -p "是否停止 Docker 基礎設施服務？(y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "   停止 Docker 服務..."
    docker compose stop mqtt-broker postgres modbus-simulator
fi

echo "✅ 完成"

