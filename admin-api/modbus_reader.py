"""Modbus 寄存器讀取服務"""
import asyncio
from pymodbus.client import AsyncModbusTcpClient
from loguru import logger
from typing import Dict, List, Optional
import struct

# 設備寄存器配置（讀取更多寄存器以顯示完整數據）
DEVICE_REGISTER_CONFIG = {
    "flow_meter": {
        "start_address": 0x0000,
        "count": 3,  # 瞬时流量 (1個) + 累積流量 (2個寄存器，32位)
    },
    "pressure_positive": {
        "start_address": 0x1000,
        "count": 2,  # 讀取更多寄存器以顯示完整數據
    },
    "pressure_vacuum": {
        "start_address": 0x1000,
        "count": 2,  # 讀取更多寄存器以顯示完整數據
    },
    "dc_meter": {
        "start_address": 0x1000,
        "count": 8,  # 電壓、電流、功率、無功功率 (每個 Int32 佔 2 個寄存器)
    },
    "ac110v_meter": {
        "start_address": 0x1000,
        "count": 8,  # 電壓、電流、功率、無功功率
    },
    "ac220v_meter": {
        "start_address": 0x1000,
        "count": 8,  # 電壓、電流、功率、無功功率
    },
    "ac220v_3p_meter": {
        "start_address": 0x1000,
        "count": 17,  # 三相電表：根據文檔 04 03 10 00 00 11 (17個寄存器)
    },
}

class ModbusReader:
    """Modbus 寄存器讀取器"""
    
    def __init__(self):
        self.clients: Dict[str, AsyncModbusTcpClient] = {}
    
    async def read_registers(self, device_id: str, device_data: dict) -> Optional[Dict]:
        """讀取設備的 Modbus 寄存器"""
        if not device_data.get("enabled", False):
            logger.debug(f"⚠️ {device_id} 未啟用，跳過讀取")
            return None
        
        device_type = device_data.get("type", "")
        config = DEVICE_REGISTER_CONFIG.get(device_id)
        
        if not config:
            logger.info(f"⚠️ {device_id} 沒有寄存器配置")
            return None
        
        host = "localhost"
        port = device_data.get("port", 5020)
        slave_id = device_data.get("slave_id", 1)
        start_address = config["start_address"]
        count = config["count"]
        
        client_key = f"{host}:{port}"
        
        try:
            # 獲取或創建客戶端
            if client_key not in self.clients:
                client = AsyncModbusTcpClient(host=host, port=port)
                await client.connect()
                self.clients[client_key] = client
            else:
                client = self.clients[client_key]
            
            # 讀取寄存器
            result = await client.read_holding_registers(
                address=start_address,
                count=count,
                device_id=slave_id
            )
            
            if result.isError():
                logger.error(f"❌ 讀取 {device_id} 寄存器失敗: {result}")
                return None
            
            logger.info(f"✅ 成功讀取 {device_id} 的寄存器: {len(result.registers)} 個")
            
            # 獲取寄存器值
            registers = result.registers
            
            # 構建完整的 Modbus 響應格式（十六進制）
            # 格式: Slave ID + Function Code + Byte Count + Data Bytes + CRC
            # 注意：pymodbus 只返回數據部分，我們需要構建完整的響應格式
            
            # 數據部分（寄存器值轉換為字節）
            data_bytes = b""
            for reg in registers:
                data_bytes += struct.pack('>H', reg)  # Big-endian 16-bit
            
            # 構建完整的 Modbus TCP 響應（簡化版，不包含 TCP 頭）
            # Slave ID (1 byte) + Function Code (1 byte) + Byte Count (1 byte) + Data (N bytes)
            function_code = 0x03  # Read Holding Registers
            byte_count = len(data_bytes)
            
            # 完整的響應數據（不包含 CRC，因為 TCP 不需要）
            full_response = struct.pack('>B', slave_id) + struct.pack('>B', function_code) + struct.pack('>B', byte_count) + data_bytes
            
            # 轉換為十六進制字符串
            hex_data = full_response.hex().upper()
            # 每兩個字符加一個空格，使其更易讀
            hex_formatted = ' '.join(hex_data[i:i+2] for i in range(0, len(hex_data), 2))
            
            # 構建寄存器地址映射（顯示每個寄存器的地址和值）
            register_map = []
            for i, reg_value in enumerate(registers):
                reg_address = start_address + i
                register_map.append({
                    "address": reg_address,
                    "address_hex": f"0x{reg_address:04X}",
                    "value": reg_value,
                    "value_hex": f"0x{reg_value:04X}",
                })
            
            return {
                "registers": registers,
                "register_map": register_map,  # 新增：每個寄存器的地址和值
                "hex_raw": hex_formatted,
                "hex_compact": hex_data,
                "hex_data_only": data_bytes.hex().upper(),  # 只有數據部分（不含響應頭）
                "start_address": start_address,
                "count": count,
                "slave_id": slave_id,
                "function_code": function_code,
                "byte_count": byte_count,
            }
        except Exception as e:
            logger.error(f"❌ 讀取 {device_id} Modbus 數據失敗: {e}", exc_info=True)
            return None
    
    async def close_all(self):
        """關閉所有連接"""
        for client in self.clients.values():
            try:
                client.close()
            except:
                pass
        self.clients.clear()

# 全域 Modbus 讀取器實例
modbus_reader = ModbusReader()

