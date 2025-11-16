#!/bin/bash
# 基礎設施測試腳本
# Test Infrastructure Script

set -e

echo "🔍 測試基礎設施服務..."

# 顏色定義
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 檢查 Docker Compose
if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}❌ docker compose 未安裝${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker Compose 已安裝${NC}"

# 檢查服務狀態
echo ""
echo "📊 檢查服務狀態..."
docker compose ps

# 測試 MQTT Broker
echo ""
echo "🔌 測試 MQTT Broker..."
if docker compose exec -T mqtt-broker mosquitto_sub -h localhost -t '$SYS/broker/uptime' -C 1 -W 5 &> /dev/null; then
    echo -e "${GREEN}✅ MQTT Broker 正常運作${NC}"
else
    echo -e "${RED}❌ MQTT Broker 無法連接${NC}"
    exit 1
fi

# 測試 PostgreSQL
echo ""
echo "🗄️  測試 PostgreSQL..."
if docker compose exec -T postgres psql -U pump_user -d pump_testing -c "SELECT version();" &> /dev/null; then
    echo -e "${GREEN}✅ PostgreSQL 正常運作${NC}"
    
    # 測試健康檢查表
    if docker compose exec -T postgres psql -U pump_user -d pump_testing -c "SELECT * FROM health_check LIMIT 1;" &> /dev/null; then
        echo -e "${GREEN}✅ 資料庫初始化成功${NC}"
    else
        echo -e "${YELLOW}⚠️  資料庫表尚未初始化${NC}"
    fi
else
    echo -e "${RED}❌ PostgreSQL 無法連接${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ 所有基礎設施服務正常運作！${NC}"



