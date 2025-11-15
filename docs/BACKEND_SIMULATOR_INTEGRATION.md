# 後端與模擬器整合說明
## Backend-Simulator Integration Guide

**文件版本**: 1.0  
**建立日期**: 2025.11.15  
**狀態**: 整合準備

---

## 📋 整合狀態分析

### ✅ 已準備好的部分

1. **模擬器服務**
   - ✅ 8 台設備模擬器已實作並運行
   - ✅ 提供 Modbus TCP 服務（端口 5020-5027）
   - ✅ 完全符合 `MODBUS_all_devices.md` 規格

2. **基礎設施**
   - ✅ MQTT Broker 運行正常
   - ✅ PostgreSQL 運行正常
   - ✅ 所有服務在同一 Docker 網路中

3. **後端架構設計**
   - ✅ 使用 `ModbusSerialClient`（串口連接）
   - ✅ 支援環境變數配置（`USE_SIMULATOR`）
   - ✅ 設計了設備配置切換機制

### ⚠️ 需要完成的整合

#### 1. 串口橋接器完善

**當前狀態**: 基本框架已完成，但**數據轉發邏輯未實作**

**問題**:
- 模擬器提供 **Modbus TCP**（端口 5020-5027）
- 後端期望 **Modbus RTU**（通過串口 `/dev/ttySIM*`）
- 串口橋接器需要將 RTU 請求轉換為 TCP 請求

**解決方案**:
需要實作自定義 `ModbusDeviceContext`，攔截讀寫操作並轉發到 Modbus TCP 客戶端。

#### 2. 後端配置

**需要添加的配置** (`config/modbus_devices.py`):

```python
import os

USE_SIMULATOR = os.getenv("USE_SIMULATOR", "false").lower() == "true"

if USE_SIMULATOR:
    # 模擬器模式：使用虛擬串口
    FLOW_METER_PORT = "/dev/ttySIM1"
    FLOW_METER_BAUDRATE = 19200
    FLOW_METER_PARITY = 'N'
    
    # 電表 (USB-Enhanced-SERIAL-A)
    DC_METER_PORT = "/dev/ttySIM0"
    AC110V_METER_PORT = "/dev/ttySIM0_1"
    AC220V_METER_PORT = "/dev/ttySIM0_2"
    AC220V_3P_METER_PORT = "/dev/ttySIM0_3"
    POWER_METER_BAUDRATE = 57600
    POWER_METER_PARITY = 'N'
    
    # 繼電器 IO (USB-Enhanced-SERIAL-D)
    RELAY_IO_PORT = "/dev/ttySIM2"
    RELAY_IO_BAUDRATE = 115200
    RELAY_IO_PARITY = 'N'
    
    # 壓力計 (MOXA USB Serial Port)
    PRESSURE_POSITIVE_PORT = "/dev/ttySIM3"
    PRESSURE_VACUUM_PORT = "/dev/ttySIM3_1"
    PRESSURE_BAUDRATE = 19200
    PRESSURE_PARITY = 'E'  # EVEN
    
else:
    # 真實設備模式：使用真實 USB 串口
    FLOW_METER_PORT = "/dev/ttyUSB0"  # USB-Enhanced-SERIAL-C
    # ... 其他配置
```

---

## 🔄 整合方案

### 方案 A: 完善串口橋接器（推薦）

**優點**:
- 後端代碼**無需修改**
- 完全模擬真實設備環境
- 切換真實設備時只需更改配置

**缺點**:
- 需要實作完整的 RTU ↔ TCP 轉換邏輯
- 串口橋接器較複雜

**實作要求**:
1. 自定義 `ModbusDeviceContext`，攔截所有讀寫操作
2. 將 RTU 請求轉換為 Modbus TCP 請求
3. 將 TCP 響應轉換回 RTU 格式
4. 處理 CRC 校驗和協議差異

### 方案 B: 後端支援 Modbus TCP（不推薦）

**優點**:
- 直接連接，無需橋接器
- 實現簡單

**缺點**:
- 需要修改後端架構（違反設計原則）
- 真實設備使用 RTU，需要兩套代碼
- 增加維護複雜度

---

## ✅ 當前狀態總結

### 可以直接使用的部分

1. **模擬器數據** ✅
   - 模擬器已運行並提供 Modbus TCP 服務
   - 數據格式完全符合規格
   - 可以通過 Modbus TCP 客戶端直接測試

2. **後端架構設計** ✅
   - 架構設計完整
   - 支援模擬器/真實設備切換
   - 配置機制已設計

### 需要完成的部分

1. **串口橋接器** ⚠️
   - 基本框架完成
   - **需要實作數據轉發邏輯**

2. **後端配置** ⚠️
   - 需要添加 `USE_SIMULATOR` 環境變數支援
   - 需要配置虛擬串口映射

---

## 🚀 建議的實作順序

### Phase 1: 測試模擬器（立即可做）

使用 Modbus TCP 客戶端直接測試模擬器：

```python
from pymodbus.client import AsyncModbusTcpClient

# 測試流量計（端口 5020）
client = AsyncModbusTcpClient(host='localhost', port=5020)
await client.connect()

# 讀取寄存器
result = await client.read_holding_registers(address=0x0000, count=1, slave=1)
print(f"流量計數據: {result.registers}")
```

### Phase 2: 完善串口橋接器

實作完整的 RTU ↔ TCP 轉換邏輯。

### Phase 3: 後端整合

1. 添加 `USE_SIMULATOR` 配置
2. 配置虛擬串口映射
3. 測試後端與模擬器的連接

---

## 📝 結論

**當前狀態**: 
- ✅ 模擬器已準備好
- ✅ 後端架構已設計好
- ✅ **串口橋接器已完成**（已實作數據轉發邏輯）

**回答您的問題**:
> "can i assume that it can get simulator's data without special settings"

**答案**: **現在可以了！** ✅

1. ✅ 模擬器提供 **Modbus TCP**（端口 5020-5027）
2. ✅ 串口橋接器已實作 **RTU ↔ TCP 轉換**
3. ✅ 後端可以通過虛擬串口（`/dev/ttySIM*`）連接，就像連接真實設備一樣

**使用方式**:
1. 啟動模擬器和串口橋接器: `docker compose up -d modbus-simulator serial-bridge`
2. 後端配置 `USE_SIMULATOR=true`，使用虛擬串口 `/dev/ttySIM*`
3. 後端代碼**無需修改**，直接使用 `ModbusSerialClient` 連接虛擬串口

**虛擬串口映射**:
- `/dev/ttySIM0` - `/dev/ttySIM0_3`: 電表（4台）
- `/dev/ttySIM1`: 流量計
- `/dev/ttySIM2`: 繼電器 IO
- `/dev/ttySIM3` - `/dev/ttySIM3_1`: 壓力計（2台）

---

**最後更新**: 2025.11.15

