# 基礎設施快速啟動指南
## Infrastructure Quick Start Guide

---

## 🚀 5 分鐘快速啟動

### 步驟 1: 準備環境變數

```bash
cd infrastructure
cp env.example .env
# 編輯 .env 文件（可選，預設值可用於開發環境）
```

### 步驟 2: 啟動服務

```bash
# 啟動所有基礎設施服務
docker compose up -d

# 查看服務狀態
docker compose ps

# 查看日誌
docker compose logs -f
```

### 步驟 3: 驗證服務

```bash
# 運行測試腳本
./test-infrastructure.sh
```

或手動測試：

```bash
# 測試 MQTT
docker compose exec mqtt-broker mosquitto_sub -h localhost -t '$SYS/broker/uptime' -C 1

# 測試 PostgreSQL
docker compose exec postgres psql -U pump_user -d pump_testing -c "SELECT version();"
```

---

## 📋 服務端口

| 服務 | 端口 | 用途 |
|------|------|------|
| MQTT Broker (TCP) | 1883 | 後端 Python 連接 |
| MQTT Broker (WebSocket) | 8083 | 前端 React 連接 |
| PostgreSQL | 5432 | 資料庫連接 |
| pgAdmin | 5050 | 資料庫管理工具（可選） |

---

## 🔧 常用命令

### 啟動/停止

```bash
# 啟動所有服務
docker compose up -d

# 停止所有服務
docker compose down

# 停止並刪除數據（⚠️ 警告）
docker compose down -v

# 重新啟動服務
docker compose restart
```

### 查看日誌

```bash
# 查看所有日誌
docker compose logs -f

# 查看特定服務日誌
docker compose logs -f mqtt-broker
docker compose logs -f postgres
```

### 進入容器

```bash
# 進入 PostgreSQL
docker compose exec postgres psql -U pump_user -d pump_testing

# 進入 MQTT Broker
docker compose exec mqtt-broker sh
```

---

## 🔗 連接資訊

### MQTT Broker

**後端 Python 連接**:
```python
broker = "localhost"
port = 1883
```

**前端 React 連接**:
```javascript
const wsUrl = "ws://localhost:8083";
```

### PostgreSQL

**連接字串**:
```
Host: localhost
Port: 5432
Database: pump_testing
User: pump_user
Password: (從 .env 文件讀取)
```

**Python 連接範例**:
```python
import asyncpg

conn = await asyncpg.connect(
    host='localhost',
    port=5432,
    user='pump_user',
    password='pump_password_change_me',
    database='pump_testing'
)
```

---

## ⚠️ 故障排除

### MQTT Broker 無法啟動

1. 檢查端口是否被佔用:
```bash
netstat -tuln | grep 1883
netstat -tuln | grep 8083
```

2. 檢查配置文件:
```bash
docker compose exec mqtt-broker cat /mosquitto/config/mosquitto.conf
```

3. 查看日誌:
```bash
docker compose logs mqtt-broker
```

### PostgreSQL 無法連接

1. 檢查服務狀態:
```bash
docker compose ps postgres
```

2. 檢查健康狀態:
```bash
docker compose exec postgres pg_isready -U pump_user
```

3. 查看日誌:
```bash
docker compose logs postgres
```

### 權限問題

確保目錄有正確權限:
```bash
chmod -R 755 mqtt/data mqtt/log
```

---

## 📚 下一步

基礎設施啟動後，可以：

1. **開發後端服務**: 連接到 MQTT Broker 和 PostgreSQL
2. **開發前端應用**: 連接到 MQTT WebSocket (Port 8083)
3. **配置資料庫**: 使用 pgAdmin 或直接連接 PostgreSQL

---

**需要幫助？** 查看 [完整 README](README.md)



