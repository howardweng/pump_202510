#!/bin/bash

# Pump App 停止腳本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PID_FILE="$APP_DIR/pump_app.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "ℹ️  Pump App 未運行（找不到 PID 文件）"
    exit 0
fi

PID=$(cat "$PID_FILE")

if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "ℹ️  Pump App 未運行（進程不存在）"
    rm -f "$PID_FILE"
    exit 0
fi

echo "🛑 正在停止 Pump App (PID: $PID)..."

# 停止進程及其子進程
pkill -P "$PID" 2>/dev/null
kill "$PID" 2>/dev/null

# 等待進程結束
for i in {1..10}; do
    if ! ps -p "$PID" > /dev/null 2>&1; then
        break
    fi
    sleep 0.5
done

# 如果還在運行，強制殺死
if ps -p "$PID" > /dev/null 2>&1; then
    echo "⚠️  強制停止進程..."
    kill -9 "$PID" 2>/dev/null
    pkill -9 -P "$PID" 2>/dev/null
fi

rm -f "$PID_FILE"

echo "✅ Pump App 已停止"

