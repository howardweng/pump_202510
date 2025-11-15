#!/bin/bash

# Pump App 啟動腳本
# 用法: ./start.sh [port] [--no-log]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$APP_DIR/logs"
LOG_FILE="$LOG_DIR/pump_app.log"
PID_FILE="$APP_DIR/pump_app.pid"
PORT=${1:-3000}

# 創建日誌目錄
mkdir -p "$LOG_DIR"

# 檢查是否已經運行
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "⚠️  Pump App 已經在運行中 (PID: $OLD_PID, Port: $PORT)"
        echo "   使用 './stop.sh' 停止服務，或使用 './logs.sh' 查看日誌"
        exit 1
    else
        rm -f "$PID_FILE"
    fi
fi

# 檢查端口是否被佔用
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":$PORT " || ss -tuln 2>/dev/null | grep -q ":$PORT "; then
    echo "❌ 端口 $PORT 已被佔用"
    echo "   請使用其他端口: ./start.sh 3001"
    exit 1
fi

echo "🚀 正在啟動 Pump App..."
echo "   目錄: $APP_DIR"
echo "   端口: $PORT"
echo "   日誌: $LOG_FILE"
echo ""

# 檢查 node_modules
if [ ! -d "$APP_DIR/node_modules" ]; then
    echo "📦 安裝依賴中..."
    cd "$APP_DIR"
    npm install
fi

# 啟動應用並記錄日誌
cd "$APP_DIR"
PORT=$PORT npm start > "$LOG_FILE" 2>&1 &
APP_PID=$!

# 保存 PID
echo $APP_PID > "$PID_FILE"

# 等待一下確認啟動
sleep 3

# 檢查進程是否還在運行
if ! ps -p "$APP_PID" > /dev/null 2>&1; then
    echo "❌ 啟動失敗！請檢查日誌: $LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
fi

echo "✅ Pump App 已啟動"
echo "   PID: $APP_PID"
echo "   URL: http://localhost:$PORT"
echo ""
echo "📋 查看日誌: ./server/logs.sh 或 ./server/server.sh logs"
echo "🛑 停止服務: ./server/stop.sh 或 ./server/server.sh stop"
echo ""

# 如果沒有 --no-log 參數，則顯示日誌
if [ "$2" != "--no-log" ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📄 實時日誌 (按 Ctrl+C 退出日誌監控，服務會繼續運行)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    tail -f "$LOG_FILE"
fi

