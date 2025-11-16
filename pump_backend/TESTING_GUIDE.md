# 後端測試指南
## Backend Testing Guide

---

## 📋 目錄

1. [環境準備](#環境準備)
2. [配置設置](#配置設置)
3. [啟動測試](#啟動測試)
4. [功能驗證](#功能驗證)
5. [常見問題](#常見問題)

---

## 🔧 環境準備

### 1. 確保基礎設施運行

```bash
# 檢查服務狀態
cd /home/datavan/pump_202510
docker compose ps

# 確保以下服務運行：
# - mqtt-broker (健康)
# - postgres (健康)
# - modbus-simulator (運行中)
```

### 2. 安裝 Python 依賴

```bash
cd pump_backend

# 創建虛擬環境（推薦）
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安裝依賴
pip install -r requirements.txt
```

### 3. 配置環境變數

```bash
# 從項目根目錄複製環境變數文件
cp ../env.example ../.env

# 編輯 .env 文件（如果需要）
nano ../.env
```

**關鍵環境變數**：
```bash
# MQTT 配置
MQTT_BROKER=localhost  # 從主機連接
MQTT_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=

# 模擬器配置
USE_SIMULATOR=true
MODBUS_SIMULATOR_HOST=localhost  # 從主機連接

# 日誌級別
LOG_LEVEL=INFO  # 或 DEBUG 用於詳細日誌
```

---

## ⚙️ 配置設置

### 1. 檢查 MODBUS 設備配置

編輯 `config/modbus_devices.py`，確保模擬器連接配置正確：

```python
# 如果使用模擬器，設備端口應該指向 Modbus TCP
# 例如：
FLOW_METER_PORT = "localhost:5020"  # Modbus TCP
# 或
FLOW_METER_PORT = "/dev/ttyUSB0"    # 真實串口
```

**注意**：由於 `serial-bridge` 暫時停用，後端需要直接使用 Modbus TCP 連接。

### 2. 更新設備配置以使用 Modbus TCP

需要修改 `config/modbus_devices.py` 以支援 Modbus TCP 連接。目前配置可能只支援串口。

**臨時解決方案**：修改 `drivers/modbus_base.py` 或創建 TCP 版本的驅動。

---

## 🚀 啟動測試

### 方法 1: 直接運行（推薦用於測試）

```bash
cd pump_backend
python main.py
```

### 方法 2: 使用 Python 模組

```bash
cd pump_backend
python -m main
```

### 預期輸出

```
✅ MQTT 已連線至 localhost:1883
🛡️ 安全監控器已啟動 (100Hz 專用執行緒)
✅ IO 模組已連線，開始 100Hz 監控...
🐕 看門狗已啟動 (超時: 0.5s)
✅ 感測器服務已啟動 (7/7 個設備連線)
✅ 控制服務已啟動
✅ 自動測試引擎已啟動
🔄 感測器輪詢迴圈已啟動
🔄 控制命令處理迴圈已啟動
🔄 自動測試引擎狀態機迴圈已啟動
🔄 數據記錄迴圈已啟動
```

---

## ✅ 功能驗證

### 1. 檢查 MQTT 連接

**使用 MQTT 客戶端訂閱主題**：

```bash
# 安裝 mosquitto-clients（如果沒有）
sudo apt-get install mosquitto-clients

# 訂閱所有主題
mosquitto_sub -h localhost -p 1883 -t 'pump/#' -v

# 或訂閱特定主題
mosquitto_sub -h localhost -p 1883 -t 'pump/sensors/#' -v
mosquitto_sub -h localhost -p 1883 -t 'pump/safety/#' -v
mosquitto_sub -h localhost -p 1883 -t 'pump/test/#' -v
```

**預期看到**：
- `pump/safety/status` - 安全監控狀態
- `pump/sensors/flow` - 流量計數據
- `pump/sensors/pressure/positive` - 正壓數據
- `pump/sensors/power/dc` - DC 電表數據
- 等等...

### 2. 測試感測器讀取

**檢查日誌輸出**：
```bash
# 應該看到感測器讀取日誌
✅ MODBUS 讀取成功 [/dev/ttySIM0]
讀取瞬時流量: 12.5 L/min
讀取壓力: 0.5 kg/cm²
```

**如果使用模擬器（Modbus TCP）**：
- 確保 `modbus-simulator` 容器運行
- 檢查端口 5020-5027 是否可訪問

### 3. 測試控制命令

**發布控制命令到 MQTT**：

```bash
# 測試閥門控制
mosquitto_pub -h localhost -p 1883 -t 'pump/control/valve' -m '{"valve": "A", "state": true}'

# 測試電源控制
mosquitto_pub -h localhost -p 1883 -t 'pump/control/power' -m '{"power_type": "dc", "state": true}'

# 測試測試命令
mosquitto_pub -h localhost -p 1883 -t 'pump/test/command' -m '{"action": "start", "config": {"test_id": "test001", "duration": 60}}'
```

**檢查日誌**：
- 應該看到命令處理日誌
- 檢查是否有錯誤訊息

### 4. 測試安全監控

**觸發緊急停止（如果使用真實設備）**：
- 按下緊急停止按鈕
- 檢查日誌是否顯示緊急停止處理

**檢查安全狀態**：
```bash
mosquitto_sub -h localhost -p 1883 -t 'pump/safety/status' -v
```

### 5. 測試自動測試引擎

**啟動測試**：
```bash
mosquitto_pub -h localhost -p 1883 -t 'pump/test/command' -m '{
  "action": "start",
  "config": {
    "test_id": "test_001",
    "auto_start": true,
    "duration": 30
  }
}'
```

**監控測試狀態**：
```bash
mosquitto_sub -h localhost -p 1883 -t 'pump/test/status' -v
```

**預期狀態轉換**：
1. `idle` → `initializing`
2. `initializing` → `ready`
3. `ready` → `running`
4. `running` → `completed`
5. `completed` → `idle`

---

## 🔍 調試技巧

### 1. 啟用詳細日誌

```bash
# 設置環境變數
export LOG_LEVEL=DEBUG

# 或編輯 .env
LOG_LEVEL=DEBUG
```

### 2. 檢查 MODBUS 連接

**測試 Modbus TCP 連接**：
```python
# 創建測試腳本 test_modbus_tcp.py
from pymodbus.client import AsyncModbusTcpClient
import asyncio

async def test():
    client = AsyncModbusTcpClient('localhost', port=5020)
    await client.connect()
    result = await client.read_holding_registers(0, 1, slave=1)
    print(f"Result: {result.registers}")
    client.close()

asyncio.run(test())
```

### 3. 檢查 MQTT 連接

```python
# 創建測試腳本 test_mqtt.py
from aiomqtt import Client
import asyncio

async def test():
    async with Client("localhost", 1883) as client:
        await client.publish("test/topic", "Hello MQTT")
        print("Message published")

asyncio.run(test())
```

### 4. 檢查數據記錄

```bash
# 檢查數據目錄
ls -la pump_backend/data/test_records/

# 查看 CSV 文件
cat pump_backend/data/test_records/test_*.csv
```

---

## ⚠️ 常見問題

### 1. MODBUS 連接失敗

**問題**：`❌ MODBUS 連線失敗`

**解決方案**：
- 檢查模擬器是否運行：`docker compose ps modbus-simulator`
- 檢查端口是否可訪問：`telnet localhost 5020`
- 確認配置使用 Modbus TCP 而非串口

### 2. MQTT 連接失敗

**問題**：`❌ MQTT 連線失敗`

**解決方案**：
- 檢查 MQTT Broker 是否運行：`docker compose ps mqtt-broker`
- 檢查端口：`telnet localhost 1883`
- 確認環境變數 `MQTT_BROKER` 設置正確

### 3. 感測器讀取失敗

**問題**：`❌ 感測器服務啟動失敗`

**解決方案**：
- 檢查所有感測器驅動配置
- 確認模擬器所有端口（5020-5027）可訪問
- 檢查日誌中的詳細錯誤訊息

### 4. 安全監控無法啟動

**問題**：`❌ IO 模組連線失敗`

**解決方案**：
- 如果使用模擬器，確認繼電器 IO 模擬器運行在端口 5027
- 檢查配置中的 `RELAY_IO_PORT` 設置
- 暫時可以跳過（不影響其他功能測試）

---

## 📊 測試檢查清單

- [ ] 基礎設施服務運行（MQTT、PostgreSQL、模擬器）
- [ ] Python 依賴安裝完成
- [ ] 環境變數配置正確
- [ ] 後端成功啟動
- [ ] MQTT 連接成功
- [ ] 感測器數據正常讀取
- [ ] 控制命令正常處理
- [ ] 安全監控正常運行
- [ ] 自動測試引擎正常運作
- [ ] 數據記錄正常保存

---

## 🎯 下一步

1. **完善 Modbus TCP 支援**：更新驅動以支援直接 TCP 連接
2. **添加單元測試**：為各個組件編寫測試用例
3. **整合測試**：測試完整的工作流程
4. **性能測試**：驗證 100Hz 安全監控性能

---

**最後更新**: 2025.11.15



