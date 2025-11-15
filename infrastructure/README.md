# 基礎設施配置目錄
## Infrastructure Configuration Directory

本目錄包含基礎設施服務的配置文件和數據目錄。

---

## 📁 目錄結構

```
infrastructure/
├── mqtt/                    # MQTT Broker 配置和數據
│   ├── config/
│   │   └── mosquitto.conf   # MQTT Broker 配置文件
│   ├── data/                # MQTT 持久化數據（自動生成）
│   └── log/                 # MQTT 日誌（自動生成）
│
└── postgres/                # PostgreSQL 配置
    └── init/
        └── 01-init.sql      # 資料庫初始化腳本
```

---

## ⚠️ 重要說明

**本目錄的配置文件被根目錄的 `docker-compose.yml` 引用。**

所有服務的啟動和管理請使用根目錄的 `docker-compose.yml`：

```bash
# 從專案根目錄執行
docker compose up -d
```

---

## 📚 相關文檔

- [專案總覽 README](../README.md)
- [後端架構設計](../docs/BACKEND_ARCHITECTURE_PLAN.md)

---

**注意**: 本目錄僅包含配置文件，不包含 Docker Compose 配置。請使用根目錄的 `docker-compose.yml`。
