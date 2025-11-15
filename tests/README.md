# 測試框架說明
## Testing Framework Documentation

---

## 📋 概述

本測試框架使用 `pytest` 進行自動化測試，支援：
- 單元測試
- 整合測試
- 異步測試
- 中文測試報告（帶時間戳）

---

## 🚀 快速開始

### 1. 安裝測試依賴

```bash
cd /home/datavan/pump_202510
pip install -r tests/requirements.txt
```

### 2. 確保基礎設施運行

```bash
# 確保模擬器和 MQTT 運行
docker compose ps

# 如果未運行，啟動它們
docker compose up -d mqtt-broker modbus-simulator
```

### 3. 運行所有測試

```bash
# 使用測試腳本（推薦）
python tests/run_tests.py

# 或直接使用 pytest
pytest tests/ -v --html=tests/reports/report.html --self-contained-html
```

---

## 📁 測試結構

```
tests/
├── conftest.py              # Pytest 配置和共享 Fixtures
├── pytest.ini               # Pytest 配置文件
├── run_tests.py             # 測試運行腳本（生成中文報告）
├── reports/                 # 測試報告目錄
│   ├── custom.css          # 報告樣式
│   └── 測試報告_*.html     # 生成的報告文件
│
├── test_modbus_base.py      # MODBUS 基礎驅動測試
├── test_flow_meter.py       # 流量計驅動測試
├── test_power_meter.py      # 電表驅動測試
├── test_pressure_sensor.py  # 壓力計驅動測試
├── test_relay_io.py         # 繼電器 IO 驅動測試
├── test_mqtt_client.py      # MQTT 客戶端測試
├── test_sensor_service.py   # 感測器服務測試
├── test_state_machine.py    # 狀態機測試
└── test_data_converter.py   # 數據轉換器測試
```

---

## 🏷️ 測試標記

使用 `pytest` 標記來分類測試：

```bash
# 只運行單元測試
pytest -m unit

# 只運行整合測試
pytest -m integration

# 只運行 MODBUS 相關測試
pytest -m modbus

# 只運行感測器測試
pytest -m sensor

# 跳過需要模擬器的測試
pytest -m "not requires_simulator"
```

---

## 📊 測試報告

### 報告位置

測試報告保存在 `tests/reports/` 目錄，文件名格式：
```
測試報告_YYYYMMDD_HHMMSS.html
```

### 查看報告

```bash
# 打開最新的報告
ls -t tests/reports/*.html | head -1 | xargs xdg-open  # Linux
# 或
open $(ls -t tests/reports/*.html | head -1)  # Mac
```

---

## 🔧 配置說明

### pytest.ini

主要配置：
- `asyncio_mode = auto` - 自動處理異步測試
- `markers` - 定義測試標記
- `log_cli = true` - 顯示日誌輸出

### conftest.py

提供共享的 fixtures：
- `event_loop` - 異步事件循環
- `test_config` - 測試配置

---

## 📝 編寫新測試

### 範例：單元測試

```python
import pytest
from pump_backend.utils.data_converter import parse_int32

@pytest.mark.unit
class TestDataConverter:
    def test_parse_int32_positive(self):
        registers = [0x0000, 0x0064]
        value = parse_int32(registers)
        assert value == 100
```

### 範例：異步測試

```python
import pytest

@pytest.mark.asyncio
@pytest.mark.modbus
@pytest.mark.requires_simulator
async def test_modbus_connection(modbus_tcp_device):
    result = await modbus_tcp_device.connect()
    assert result is True
```

---

## ⚠️ 注意事項

1. **需要模擬器運行的測試**：標記為 `@pytest.mark.requires_simulator`
2. **需要 MQTT 的測試**：標記為 `@pytest.mark.requires_mqtt`
3. **異步測試**：使用 `@pytest.mark.asyncio` 裝飾器
4. **測試隔離**：每個測試應該獨立，不依賴其他測試的狀態

---

## 🐛 調試測試

```bash
# 顯示詳細輸出
pytest -v -s

# 只運行失敗的測試
pytest --lf

# 運行特定測試文件
pytest tests/test_flow_meter.py

# 運行特定測試函數
pytest tests/test_flow_meter.py::TestFlowMeter::test_read_instantaneous_flow
```

---

**最後更新**: 2025.11.15

