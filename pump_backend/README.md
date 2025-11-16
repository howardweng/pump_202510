# 幫浦測試平台後端
## Pump Testing Platform Backend

**版本**: 1.0.0  
**狀態**: 開發中

---

## 📋 專案說明

幫浦測試平台的後端服務，負責：
- MODBUS RTU 設備通訊
- 安全監控（100Hz）
- 感測器數據收集
- 設備控制（閥門、電源）
- 自動測試流程
- MQTT 訊息發布/訂閱

---

## 🚀 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 配置環境變數

```bash
cp .env.example .env
# 編輯 .env 文件，配置 MQTT 和設備連接
```

### 3. 啟動服務

```bash
python main.py
```

---

## 📁 專案結構

```
pump_backend/
├── config/          # 配置管理
├── core/            # 核心框架
├── drivers/         # 硬體驅動層
├── services/        # 業務邏輯層
├── models/          # 資料模型
├── utils/           # 工具函數
├── tests/           # 測試程式碼
├── logs/            # 日誌目錄
└── data/            # 數據目錄
```

---

## 🔧 配置說明

### 模擬器模式

設置 `USE_SIMULATOR=true` 使用模擬器進行開發測試。

### 真實設備模式

設置 `USE_SIMULATOR=false` 並配置真實串口路徑。

---

## 📚 文檔

詳細架構設計請參考：
- [後端架構設計](docs/BACKEND_ARCHITECTURE_PLAN.md)
- [MODBUS 設備規格](docs/MODBUS_all_devices.md)
- [模擬器整合說明](docs/BACKEND_SIMULATOR_INTEGRATION.md)

---

## 🧪 測試

```bash
# 運行所有測試
pytest

# 運行特定測試
pytest tests/test_modbus.py
```

---

## 📝 開發階段

當前階段：**Phase 0 - 風險驗證**

---

**最後更新**: 2025.11.15



