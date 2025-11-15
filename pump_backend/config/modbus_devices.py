"""MODBUS 設備配置"""
import os
from typing import Dict, Any
from config.settings import settings


def get_device_config() -> Dict[str, Dict[str, Any]]:
    """
    獲取設備配置
    
    Returns:
        設備配置字典
    """
    if settings.USE_SIMULATOR:
        # 模擬器模式：使用虛擬串口
        return {
            "flow_meter": {
                "port": os.getenv("FLOW_METER_PORT", "/dev/ttySIM1"),
                "baudrate": int(os.getenv("FLOW_METER_BAUDRATE", "19200")),
                "parity": os.getenv("FLOW_METER_PARITY", "N"),
                "stopbits": 1,
                "bytesize": 8,
                "slave_id": int(os.getenv("FLOW_METER_SLAVE_ID", "1")),
                "timeout": 1.0
            },
            "dc_meter": {
                "port": os.getenv("DC_METER_PORT", "/dev/ttySIM0"),
                "baudrate": int(os.getenv("DC_METER_BAUDRATE", "57600")),
                "parity": os.getenv("DC_METER_PARITY", "N"),
                "stopbits": 1,
                "bytesize": 8,
                "slave_id": int(os.getenv("DC_METER_SLAVE_ID", "1")),
                "timeout": 1.0
            },
            "ac110v_meter": {
                "port": os.getenv("AC110V_METER_PORT", "/dev/ttySIM0_1"),
                "baudrate": int(os.getenv("AC110V_METER_BAUDRATE", "57600")),
                "parity": os.getenv("AC110V_METER_PARITY", "N"),
                "stopbits": 1,
                "bytesize": 8,
                "slave_id": int(os.getenv("AC110V_METER_SLAVE_ID", "2")),
                "timeout": 1.0
            },
            "ac220v_meter": {
                "port": os.getenv("AC220V_METER_PORT", "/dev/ttySIM0_2"),
                "baudrate": int(os.getenv("AC220V_METER_BAUDRATE", "57600")),
                "parity": os.getenv("AC220V_METER_PARITY", "N"),
                "stopbits": 1,
                "bytesize": 8,
                "slave_id": int(os.getenv("AC220V_METER_SLAVE_ID", "3")),
                "timeout": 1.0
            },
            "ac220v_3p_meter": {
                "port": os.getenv("AC220V_3P_METER_PORT", "/dev/ttySIM0_3"),
                "baudrate": int(os.getenv("AC220V_3P_METER_BAUDRATE", "57600")),
                "parity": os.getenv("AC220V_3P_METER_PARITY", "N"),
                "stopbits": 1,
                "bytesize": 8,
                "slave_id": int(os.getenv("AC220V_3P_METER_SLAVE_ID", "4")),
                "timeout": 1.0
            },
            "relay_io": {
                "port": os.getenv("RELAY_IO_PORT", "/dev/ttySIM2"),
                "baudrate": int(os.getenv("RELAY_IO_BAUDRATE", "115200")),
                "parity": os.getenv("RELAY_IO_PARITY", "N"),
                "stopbits": 1,
                "bytesize": 8,
                "slave_id": int(os.getenv("RELAY_IO_SLAVE_ID", "1")),
                "timeout": 1.0
            },
            "pressure_positive": {
                "port": os.getenv("PRESSURE_POSITIVE_PORT", "/dev/ttySIM3"),
                "baudrate": int(os.getenv("PRESSURE_POSITIVE_BAUDRATE", "19200")),
                "parity": os.getenv("PRESSURE_POSITIVE_PARITY", "E"),
                "stopbits": 1,
                "bytesize": 8,
                "slave_id": int(os.getenv("PRESSURE_POSITIVE_SLAVE_ID", "2")),
                "timeout": 1.0
            },
            "pressure_vacuum": {
                "port": os.getenv("PRESSURE_VACUUM_PORT", "/dev/ttySIM3_1"),
                "baudrate": int(os.getenv("PRESSURE_VACUUM_BAUDRATE", "19200")),
                "parity": os.getenv("PRESSURE_VACUUM_PARITY", "E"),
                "stopbits": 1,
                "bytesize": 8,
                "slave_id": int(os.getenv("PRESSURE_VACUUM_SLAVE_ID", "3")),
                "timeout": 1.0
            }
        }
    else:
        # 真實設備模式：使用真實 USB 串口
        return {
            "flow_meter": {
                "port": os.getenv("FLOW_METER_PORT", "/dev/ttyUSB0"),
                "baudrate": int(os.getenv("FLOW_METER_BAUDRATE", "19200")),
                "parity": os.getenv("FLOW_METER_PARITY", "N"),
                "stopbits": 1,
                "bytesize": 8,
                "slave_id": int(os.getenv("FLOW_METER_SLAVE_ID", "1")),
                "timeout": 1.0
            },
            # ... 其他設備配置（真實串口）
            # 注意：真實設備的串口映射需要根據實際硬體配置
        }

