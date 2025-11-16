"""JX3101 單相電表模擬器和 JX8304M 三相電表模擬器"""
from .base import BaseModbusSimulator
import asyncio
import struct
from loguru import logger


class SinglePhasePowerMeterSimulator(BaseModbusSimulator):
    """JX3101 單相電表模擬器 (DC/AC110V/AC220V)
    
    根據 MODBUS_all_devices.md:
    - RTU 地址: 1 (DC), 2 (AC110V), 3 (AC220V)
    - 寄存器地址: 0x1000 開始
    - 所有參數都是 Signed Int32 (2 個寄存器, 4 bytes)
    - 電壓: 0x1000-0x1001, ÷ 100
    - 電流: 0x1002-0x1003, ÷ 1000
    - 有功功率: 0x1004-0x1005, ÷ 10000
    - 無功功率: 0x1006-0x1007, ÷ 10000
    - 輪詢頻率: 2 Hz
    """
    
    def __init__(self, slave_id: int, port: int, meter_type: str = "DC"):
        """
        Args:
            slave_id: RTU 地址 (1=DC, 2=AC110V, 3=AC220V)
            port: Modbus TCP 端口
            meter_type: "DC", "AC110V", "AC220V"
        """
        self.meter_type = meter_type
        config = {
            'voltage': 0.0,      # V
            'current': 0.0,      # A
            'active_power': 0.0, # kW
            'reactive_power': 0.0, # kVAR
            'enabled': True
        }
        super().__init__(slave_id, port, config)
        
        # 初始化所有寄存器
        self._update_int32_register(0x1000, 0)  # 電壓
        self._update_int32_register(0x1002, 0)  # 電流
        self._update_int32_register(0x1004, 0)  # 有功功率
        self._update_int32_register(0x1006, 0)  # 無功功率
    
    def _update_int32_register(self, start_address: int, value: int):
        """
        更新 Int32 寄存器（2 個寄存器，4 bytes）
        
        根據規格: Big-Endian, 高位在前
        """
        # 確保值在 Int32 範圍內
        value = max(-2147483648, min(2147483647, value))
        
        # 轉換為 4 bytes (Big-Endian)
        bytes_data = struct.pack('>i', value)  # '>i' = big-endian signed int32
        
        # 拆分為 2 個 16 位元寄存器
        high_word = (bytes_data[0] << 8) | bytes_data[1]
        low_word = (bytes_data[2] << 8) | bytes_data[3]
        
        self.update_register(start_address, high_word)
        self.update_register(start_address + 1, low_word)
    
    async def simulate_loop(self):
        """模擬數據更新迴圈 (2Hz = 0.5秒)"""
        while self._running:
            if self.config.get('enabled', True):
                # 根據規格換算公式
                # 電壓: 實際值 × 100
                voltage_raw = int(self.config.get('voltage', 0.0) * 100)
                self._update_int32_register(0x1000, voltage_raw)
                
                # 電流: 實際值 × 1000
                current_raw = int(self.config.get('current', 0.0) * 1000)
                self._update_int32_register(0x1002, current_raw)
                
                # 有功功率: 實際值 × 10000
                power_raw = int(self.config.get('active_power', 0.0) * 10000)
                self._update_int32_register(0x1004, power_raw)
                
                # 無功功率: 實際值 × 10000
                reactive_power_raw = int(self.config.get('reactive_power', 0.0) * 10000)
                self._update_int32_register(0x1006, reactive_power_raw)
            
            await asyncio.sleep(0.5)  # 2Hz 更新
    
    def set_voltage(self, value: float):
        """設定電壓 (V)"""
        self.config['voltage'] = value
        logger.debug(f"{self.meter_type} 電表電壓已更新: {value} V")
    
    def set_current(self, value: float):
        """設定電流 (A)"""
        self.config['current'] = value
        logger.debug(f"{self.meter_type} 電表電流已更新: {value} A")
    
    def set_active_power(self, value: float):
        """設定有功功率 (kW)"""
        self.config['active_power'] = value
        logger.debug(f"{self.meter_type} 電表有功功率已更新: {value} kW")


class ThreePhasePowerMeterSimulator(BaseModbusSimulator):
    """JX8304M 三相電表模擬器
    
    根據 MODBUS_all_devices.md:
    - RTU 地址: 4
    - 寄存器地址: 0x1000 開始
    - 所有參數都是 Signed Int32 (2 個寄存器, 4 bytes)
    - 讀取指令: 04 03 10 00 00 11 (17 個寄存器, 34 bytes)
    - 輪詢頻率: 2 Hz
    """
    
    def __init__(self, slave_id: int = 4, port: int = 5024):
        config = {
            'voltage_a': 220.0,  # V
            'voltage_b': 220.0,  # V
            'voltage_c': 220.0,  # V
            'current_a': 0.0,    # A
            'current_b': 0.0,    # A
            'current_c': 0.0,    # A
            'current_n': 0.0,    # A (漏電流)
            'power_a': 0.0,      # kW
            'power_b': 0.0,      # kW
            'power_c': 0.0,      # kW
            'power_total': 0.0,  # kW (合相功率)
            'enabled': True
        }
        super().__init__(slave_id, port, config)
        
        # 初始化所有寄存器
        self._init_registers()
    
    def _init_registers(self):
        """初始化所有寄存器"""
        # A/B/C 相電壓 (0x1000-0x1005)
        self._update_int32_register(0x1000, 0)  # A相電壓
        self._update_int32_register(0x1002, 0)  # B相電壓
        self._update_int32_register(0x1004, 0)  # C相電壓
        
        # A/B/C/0 相電流 (0x1006-0x100D)
        self._update_int32_register(0x1006, 0)  # A相電流
        self._update_int32_register(0x1008, 0)  # B相電流
        self._update_int32_register(0x100A, 0)  # C相電流
        self._update_int32_register(0x100C, 0)  # 0相電流（漏電流）
        
        # A/B/C 相功率 + 合相功率 (0x100E-0x1015)
        self._update_int32_register(0x100E, 0)  # A相功率
        self._update_int32_register(0x1010, 0)  # B相功率
        self._update_int32_register(0x1012, 0)  # C相功率
        self._update_int32_register(0x1014, 0)  # 合相功率
    
    def _update_int32_register(self, start_address: int, value: int):
        """更新 Int32 寄存器（Big-Endian）"""
        value = max(-2147483648, min(2147483647, value))
        bytes_data = struct.pack('>i', value)
        high_word = (bytes_data[0] << 8) | bytes_data[1]
        low_word = (bytes_data[2] << 8) | bytes_data[3]
        self.update_register(start_address, high_word)
        self.update_register(start_address + 1, low_word)
    
    async def simulate_loop(self):
        """模擬數據更新迴圈 (2Hz)"""
        while self._running:
            if self.config.get('enabled', True):
                # 根據規格換算公式
                # 電壓: ÷ 100, 電流: ÷ 1000, 功率: ÷ 10000
                
                # 更新電壓
                self._update_int32_register(0x1000, int(self.config['voltage_a'] * 100))
                self._update_int32_register(0x1002, int(self.config['voltage_b'] * 100))
                self._update_int32_register(0x1004, int(self.config['voltage_c'] * 100))
                
                # 更新電流
                self._update_int32_register(0x1006, int(self.config['current_a'] * 1000))
                self._update_int32_register(0x1008, int(self.config['current_b'] * 1000))
                self._update_int32_register(0x100A, int(self.config['current_c'] * 1000))
                self._update_int32_register(0x100C, int(self.config['current_n'] * 1000))
                
                # 更新功率
                self._update_int32_register(0x100E, int(self.config['power_a'] * 10000))
                self._update_int32_register(0x1010, int(self.config['power_b'] * 10000))
                self._update_int32_register(0x1012, int(self.config['power_c'] * 10000))
                self._update_int32_register(0x1014, int(self.config['power_total'] * 10000))
            
            await asyncio.sleep(0.5)  # 2Hz 更新



