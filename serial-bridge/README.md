# 串口橋接器服務
## Serial Bridge Service

## 功能說明

將 Modbus TCP 模擬器轉換為虛擬串口，讓後端可以通過串口連接模擬器。

**核心功能**:
- ✅ 創建虛擬串口（使用 `pty`）
- ✅ 運行 Modbus RTU 服務器
- ✅ **自動轉發 RTU 請求到 Modbus TCP**（已實作）
- ✅ 支援所有功能碼（0x01-0x10）
- ✅ 線程安全的異步轉發

## 虛擬串口映射

| 虛擬串口 | TCP 端口 | 設備 | Slave ID | UART 設定 |
|---------|---------|------|----------|-----------|
| /dev/ttySIM0 | 5021 | DC 電表 | 1 | 57600/8/NONE/1 |
| /dev/ttySIM0_1 | 5022 | AC110V 電表 | 2 | 57600/8/NONE/1 |
| /dev/ttySIM0_2 | 5023 | AC220V 電表 | 3 | 57600/8/NONE/1 |
| /dev/ttySIM0_3 | 5024 | AC220V 3P 電表 | 4 | 57600/8/NONE/1 |
| /dev/ttySIM1 | 5020 | 流量計 | 1 | 19200/8/NONE/1 |
| /dev/ttySIM2 | 5027 | 繼電器 IO | 1 | 115200/8/NONE/1 |
| /dev/ttySIM3 | 5025 | 壓力計 (正壓) | 2 | 19200/8/EVEN/1 |
| /dev/ttySIM3_1 | 5026 | 壓力計 (真空) | 3 | 19200/8/EVEN/1 |

## 技術實作

### 轉發機制

使用自定義 `ForwardingModbusContext` 類別：
- 攔截所有 `getValues()` 和 `setValues()` 調用
- 自動將 RTU 請求轉換為 Modbus TCP 請求
- 將 TCP 響應轉換回 RTU 格式
- 支援線程安全的異步操作

### 支援的功能碼

**讀取操作**:
- `0x01`: Read Coils
- `0x02`: Read Discrete Inputs
- `0x03`: Read Holding Registers
- `0x04`: Read Input Registers

**寫入操作**:
- `0x05`: Write Single Coil
- `0x06`: Write Single Register
- `0x0F`: Write Multiple Coils
- `0x10`: Write Multiple Registers

## 使用方式

```bash
# 啟動服務（需要先啟動模擬器）
docker compose up -d modbus-simulator serial-bridge

# 查看日誌
docker compose logs -f serial-bridge

# 測試連接（從主機）
# 注意：虛擬串口在容器內，需要通過容器訪問
docker compose exec serial-bridge ls -la /dev/ttySIM*
```

## 後端整合

後端可以像連接真實設備一樣連接虛擬串口：

```python
from pymodbus.client import ModbusSerialClient

# 連接虛擬串口（在容器內）
client = ModbusSerialClient(
    port='/dev/ttySIM1',  # 流量計
    baudrate=19200,
    parity='N',
    stopbits=1,
    bytesize=8
)

# 讀取寄存器
result = client.read_holding_registers(address=0x0000, count=1, slave=1)
```

## 注意事項

1. **特權模式**: 需要 `privileged: true` 來創建虛擬串口
2. **容器內訪問**: 虛擬串口在容器內，後端也需要在容器內運行或通過 volume 映射
3. **事件循環**: 使用線程安全的異步調用機制，確保在同步上下文中也能正常工作
