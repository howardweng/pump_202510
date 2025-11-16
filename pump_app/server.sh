#!/bin/bash

# Pump App 服務器管理腳本
# 用法: ./server.sh [start|stop|restart|status|logs]

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_DIR="$APP_DIR"

case "$1" in
    start)
        PORT=${2:-3000}
        "$SCRIPT_DIR/start.sh" "$PORT"
        ;;
    stop)
        "$SCRIPT_DIR/stop.sh"
        ;;
    restart)
        "$SCRIPT_DIR/stop.sh"
        sleep 2
        PORT=${2:-3000}
        "$SCRIPT_DIR/start.sh" "$PORT"
        ;;
    status)
        PID_FILE="$APP_DIR/pump_app.pid"
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p "$PID" > /dev/null 2>&1; then
                PORT=$(lsof -p "$PID" 2>/dev/null | grep LISTEN | awk '{print $9}' | cut -d: -f2 | head -1)
                echo "✅ Pump App 正在運行"
                echo "   PID: $PID"
                echo "   端口: ${PORT:-未知}"
                echo "   URL: http://localhost:${PORT:-3000}"
            else
                echo "❌ Pump App 未運行（PID 文件存在但進程不存在）"
                rm -f "$PID_FILE"
            fi
        else
            echo "❌ Pump App 未運行"
        fi
        ;;
    logs)
        shift
        "$SCRIPT_DIR/logs.sh" "$@"
        ;;
    *)
        echo "Pump App 服務器管理腳本"
        echo ""
        echo "用法: $0 {start|stop|restart|status|logs} [選項]"
        echo ""
        echo "命令:"
        echo "  start [port]    啟動服務器（預設端口: 3000）"
        echo "  stop            停止服務器"
        echo "  restart [port]  重啟服務器"
        echo "  status          查看服務器狀態"
        echo "  logs [選項]     查看日誌"
        echo ""
        echo "日誌選項:"
        echo "  --tail N        顯示最後 N 行（預設: 50）"
        echo "  --follow, -f    實時跟隨日誌"
        echo "  --error, -e     只顯示錯誤日誌"
        echo ""
        echo "範例:"
        echo "  $0 start 3000"
        echo "  $0 logs --follow"
        echo "  $0 logs --error"
        echo "  $0 status"
        exit 1
        ;;
esac



