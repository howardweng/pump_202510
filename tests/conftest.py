"""Pytest 配置和共享 Fixtures"""
import pytest
import asyncio
import sys
from pathlib import Path

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "pump_backend"))

# 確保 markdown_report 插件被載入
pytest_plugins = ["tests.markdown_report"]


@pytest.fixture(scope="session")
def event_loop():
    """創建事件循環供所有測試使用"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_config():
    """測試配置"""
    return {
        "mqtt_broker": "localhost",
        "mqtt_port": 1883,
        "modbus_simulator_host": "localhost",
        "modbus_ports": {
            "flow_meter": 5020,
            "dc_meter": 5021,
            "ac110v_meter": 5022,
            "ac220v_meter": 5023,
            "ac220v_3p_meter": 5024,
            "pressure_positive": 5025,
            "pressure_vacuum": 5026,
            "relay_io": 5027
        }
    }

