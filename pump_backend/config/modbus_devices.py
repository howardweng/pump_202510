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
        # 模擬器模式：使用 Modbus TCP（因為 serial-bridge 暫時停用）
        tcp_host = os.getenv("MODBUS_SIMULATOR_HOST", "localhost")
        return {
            "flow_meter": {
                "port": tcp_host,
                "tcp_port": int(os.getenv("FLOW_METER_TCP_PORT", "5020")),
                "use_tcp": True,
                "baudrate": 19200,  # 保留用於兼容性
                "parity": "N",
                "stopbits": 1,
                "bytesize": 8,
                "slave_id": int(os.getenv("FLOW_METER_SLAVE_ID", "1")),
                "timeout": 1.0
            },
            "dc_meter": {
                "port": tcp_host,
                "tcp_port": int(os.getenv("DC_METER_TCP_PORT", "5021")),
                "use_tcp": True,
                "baudrate": 57600,
                "parity": "N",
                "stopbits": 1,
                "bytesize": 8,
                "slave_id": int(os.getenv("DC_METER_SLAVE_ID", "1")),
                "timeout": 1.0
            },
            "ac110v_meter": {
                "port": tcp_host,
                "tcp_port": int(os.getenv("AC110V_METER_TCP_PORT", "5022")),
                "use_tcp": True,
                "baudrate": 57600,
                "parity": "N",
                "stopbits": 1,
                "bytesize": 8,
                "slave_id": int(os.getenv("AC110V_METER_SLAVE_ID", "2")),
                "timeout": 1.0
            },
            "ac220v_meter": {
                "port": tcp_host,
                "tcp_port": int(os.getenv("AC220V_METER_TCP_PORT", "5023")),
                "use_tcp": True,
                "baudrate": 57600,
                "parity": "N",
                "stopbits": 1,
                "bytesize": 8,
                "slave_id": int(os.getenv("AC220V_METER_SLAVE_ID", "3")),
                "timeout": 1.0
            },
            "ac220v_3p_meter": {
                "port": tcp_host,
                "tcp_port": int(os.getenv("AC220V_3P_METER_TCP_PORT", "5024")),
                "use_tcp": True,
                "baudrate": 57600,
                "parity": "N",
                "stopbits": 1,
                "bytesize": 8,
                "slave_id": int(os.getenv("AC220V_3P_METER_SLAVE_ID", "4")),
                "timeout": 1.0
            },
            "relay_io": {
                "port": tcp_host,
                "tcp_port": int(os.getenv("RELAY_IO_TCP_PORT", "5027")),
                "use_tcp": True,
                "baudrate": 115200,
                "parity": "N",
                "stopbits": 1,
                "bytesize": 8,
                "slave_id": int(os.getenv("RELAY_IO_SLAVE_ID", "1")),
                "timeout": 1.0
            },
            "pressure_positive": {
                "port": tcp_host,
                "tcp_port": int(os.getenv("PRESSURE_POSITIVE_TCP_PORT", "5025")),
                "use_tcp": True,
                "baudrate": 19200,
                "parity": "E",
                "stopbits": 1,
                "bytesize": 8,
                "slave_id": int(os.getenv("PRESSURE_POSITIVE_SLAVE_ID", "2")),
                "timeout": 1.0
            },
            "pressure_vacuum": {
                "port": tcp_host,
                "tcp_port": int(os.getenv("PRESSURE_VACUUM_TCP_PORT", "5026")),
                "use_tcp": True,
                "baudrate": 19200,
                "parity": "E",
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

