#!/bin/bash

# Pump App 日誌查看腳本
# 用法: ./logs.sh [--tail N] [--follow] [--error]

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$APP_DIR/logs/pump_app.log"

if [ ! -f "$LOG_FILE" ]; then
    echo "❌ 日誌文件不存在: $LOG_FILE"
    echo "   請先啟動應用: ./start.sh"
    exit 1
fi

# 解析參數
FOLLOW=false
LINES=50
ERROR_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --tail|-n)
            LINES="$2"
            shift 2
            ;;
        --follow|-f)
            FOLLOW=true
            shift
            ;;
        --error|-e)
            ERROR_ONLY=true
            shift
            ;;
        *)
            echo "用法: $0 [--tail N] [--follow] [--error]"
            echo "  --tail N, -n N    顯示最後 N 行（預設: 50）"
            echo "  --follow, -f      實時跟隨日誌"
            echo "  --error, -e       只顯示錯誤日誌"
            exit 1
            ;;
    esac
done

echo "📄 Pump App 日誌"
echo "   文件: $LOG_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ "$ERROR_ONLY" = true ]; then
    if [ "$FOLLOW" = true ]; then
        tail -f "$LOG_FILE" | grep -i --color=always -E "error|fail|warn|exception"
    else
        tail -n "$LINES" "$LOG_FILE" | grep -i --color=always -E "error|fail|warn|exception"
    fi
elif [ "$FOLLOW" = true ]; then
    tail -f -n "$LINES" "$LOG_FILE"
else
    tail -n "$LINES" "$LOG_FILE"
fi

