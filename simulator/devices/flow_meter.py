"""AFM07 流量計模擬器"""
from .base import BaseModbusSimulator
import asyncio
from loguru import logger


class FlowMeterSimulator(BaseModbusSimulator):
    """AFM07 流量計模擬器
    
    根據 MODBUS_all_devices.md:
    - RTU 地址: 1
    - 寄存器地址: 0x0000 (瞬时流量), 0x0001-0x0002 (累計流量)
    - 數據類型: Unsigned Int16 (瞬时), Unsigned Int32 (累計)
    - 換算公式: ÷ 10
    - 輪詢頻率: 1 Hz
    """
    
    def __init__(self, slave_id: int = 1, port: int = 5020):
        config = {
            'instantaneous_flow': 0.0,  # L/min
            'cumulative_flow': 0.0,     # L
            'enabled': True
        }
        super().__init__(slave_id, port, config)
        
        # 初始化寄存器
        # 0x0000: 瞬时流量 (Unsigned Int16, 倍數 10)
        # 0x0001-0x0002: 累計流量 (Unsigned Int32, 倍數 10)
        self.update_register(0x0000, 0)
        self.update_register(0x0001, 0)
        self.update_register(0x0002, 0)
    
    async def simulate_loop(self):
        """模擬數據更新迴圈 (1Hz)"""
        while self._running:
            if self.config.get('enabled', True):
                # 更新瞬时流量 (0-50 L/min)
                instant_flow = self.config.get('instantaneous_flow', 0.0)
                instant_flow_raw = int(instant_flow * 10)  # 倍數 10
                instant_flow_raw = max(0, min(65535, instant_flow_raw))  # 限制在 UInt16 範圍
                self.update_register(0x0000, instant_flow_raw)
                
                # 更新累計流量
                cumulative_flow = self.config.get('cumulative_flow', 0.0)
                cumulative_flow_raw = int(cumulative_flow * 10)
                # 拆分為高 16 位和低 16 位
                high_word = (cumulative_flow_raw >> 16) & 0xFFFF
                low_word = cumulative_flow_raw & 0xFFFF
                self.update_register(0x0001, high_word)
                self.update_register(0x0002, low_word)
            
            await asyncio.sleep(1.0)  # 1Hz 更新
    
    def set_instantaneous_flow(self, value: float):
        """設定瞬时流量 (L/min)"""
        self.config['instantaneous_flow'] = max(0.0, min(50.0, value))
        logger.debug(f"流量計瞬时流量已更新: {value} L/min")
    
    def set_cumulative_flow(self, value: float):
        """設定累計流量 (L)"""
        self.config['cumulative_flow'] = max(0.0, value)
        logger.debug(f"流量計累計流量已更新: {value} L")

