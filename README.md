# 幫浦測試平台
## Pump Testing Platform

---

## 📋 專案概述

本專案是一個幫浦測試平台系統，包含前端、後端、基礎設施和模擬器等組件。

---

## 🏗️ 專案結構

```
pump_202510/
├── docker-compose.yml          # 統一 Docker Compose 配置
├── .env.example                # 環境變數範例
├── README.md                   # 本文件
│
├── infrastructure/             # 基礎設施配置
│   ├── mqtt/                   # MQTT Broker 配置
│   └── postgres/               # PostgreSQL 配置
│
├── pump_backend/               # 後端服務 (TODO)
│   └── ...
│
├── pump_app/                   # 前端應用
│   └── ...
│
├── simulator/                  # 模擬器服務 (TODO)
│   └── ...
│
└── docs/                       # 文檔
    ├── PRD.md                  # 產品需求文檔
    ├── BACKEND_ARCHITECTURE_PLAN.md
    ├── MODBUS_all_devices.md
    └── ...
```

---

## 🚀 快速開始

### 1. 準備環境

```bash
# 複製環境變數文件
cp env.example .env

# 編輯環境變數（可選，預設值可用於開發環境）
nano .env
```

### 2. 啟動基礎設施

```bash
# 啟動所有基礎設施服務（MQTT + PostgreSQL）
docker compose up -d

# 查看服務狀態
docker compose ps

# 查看日誌
docker compose logs -f
```

### 3. 啟動特定服務

```bash
# 只啟動基礎設施
docker compose up -d mqtt-broker postgres

# 啟動包含 pgAdmin（資料庫管理工具）
docker compose --profile tools up -d
```

### 4. 停止服務

```bash
# 停止所有服務
docker compose down

# 停止並刪除數據卷（⚠️ 警告：會刪除所有數據）
docker compose down -v
```

---

## 📦 服務說明

### 基礎設施服務

| 服務 | 端口 | 說明 |
|------|------|------|
| **MQTT Broker** | 1883 (TCP)<br>8083 (WebSocket) | 訊息匯流排，用於前後端通訊 |
| **PostgreSQL** | 5432 | 資料庫，儲存測試數據和歷史記錄 |
| **pgAdmin** | 5050 | 資料庫管理工具（可選） |

### 後端服務 (TODO)

- Python 後端服務
- MODBUS 設備驅動
- 安全監控服務

### 前端服務 (TODO)

- React 前端應用
- 即時數據顯示
- 測試控制介面

### 模擬器服務 (TODO)

- MODBUS 設備模擬器
- 虛擬串口橋接器
- Admin UI

---

## 🔧 配置說明

### 環境變數

主要環境變數定義在 `.env` 文件中：

- **PostgreSQL**: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- **pgAdmin**: `PGADMIN_EMAIL`, `PGADMIN_PASSWORD`
- **MQTT**: 預設使用 localhost，無需配置

### 網路配置

所有服務都在 `pump-network` 網路中，可以通過服務名稱互相訪問：

- MQTT Broker: `mqtt-broker`
- PostgreSQL: `postgres`
- pgAdmin: `pgadmin`

---

## 🔗 連接資訊

### MQTT Broker

**後端 Python 連接**:
```python
broker = "mqtt-broker"  # 從容器內
# 或
broker = "localhost"    # 從主機
port = 1883
```

**前端 React 連接**:
```javascript
const wsUrl = "ws://localhost:8083";
```

### PostgreSQL

**連接字串**:
```
Host: postgres (從容器內) 或 localhost (從主機)
Port: 5432
Database: pump_testing (預設)
User: pump_user (預設)
Password: (從 .env 文件讀取)
```

**Python 連接範例**:
```python
import asyncpg

conn = await asyncpg.connect(
    host='postgres',  # 從容器內使用服務名稱
    port=5432,
    user='pump_user',
    password='pump_password_change_me',
    database='pump_testing'
)
```

---

## 📚 文檔

- [產品需求文檔](docs/PRD.md)
- [後端架構設計](docs/BACKEND_ARCHITECTURE_PLAN.md)
- [MODBUS 設備規格](docs/MODBUS_all_devices.md)
- [模擬器架構設計](docs/SIMULATOR_ARCHITECTURE.md)
- [基礎設施文檔](infrastructure/README.md)

---

## 🛠️ 開發指南

### 添加新服務

1. 在 `docker-compose.yml` 中添加服務定義
2. 在 `.env.example` 中添加相關環境變數
3. 更新本 README 文件

### 測試服務

```bash
# 測試 MQTT
docker compose exec mqtt-broker mosquitto_sub -h localhost -t '$SYS/broker/uptime' -C 1

# 測試 PostgreSQL
docker compose exec postgres psql -U pump_user -d pump_testing -c "SELECT version();"
```

---

## ⚠️ 注意事項

1. **數據持久化**: 所有數據都保存在 Docker volumes 中
2. **端口衝突**: 確保端口 1883, 8083, 5432, 5050 未被佔用
3. **環境變數**: 生產環境請修改 `.env` 中的預設密碼
4. **網路隔離**: 所有服務都在 `pump-network` 網路中

---

## 📝 更新日誌

- **2025.11.15**: 創建統一 Docker Compose 配置，整合基礎設施服務

---

**最後更新**: 2025.11.15

