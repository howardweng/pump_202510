"""Delta DPA 壓力計模擬器"""
from .base import BaseModbusSimulator
import asyncio
from loguru import logger


class PressureSensorSimulator(BaseModbusSimulator):
    """Delta DPA 壓力計模擬器
    
    根據 MODBUS_all_devices.md:
    - RTU 地址: 2 (正壓), 3 (真空)
    - 寄存器地址: 0x1000 (PV 值)
    - 數據類型: Unsigned Int16
    - 換算公式: × 0.1
    - 輪詢頻率: 1 Hz
    - 正壓範圍: 0 ~ 10 kg/cm² (0 ~ 1.0 MPa)
    - 真空範圍: 0 ~ -100 kPa (0 ~ -0.1 MPa)
    """
    
    def __init__(self, slave_id: int, port: int, is_vacuum: bool = False):
        """
        Args:
            slave_id: RTU 地址 (2=正壓, 3=真空)
            port: Modbus TCP 端口
            is_vacuum: True=真空, False=正壓
        """
        self.is_vacuum = is_vacuum
        config = {
            'pressure': 0.0,  # kg/cm² (正壓) 或 kPa (真空)
            'enabled': True
        }
        super().__init__(slave_id, port, config)
        
        # 初始化寄存器 0x1000
        self.update_register(0x1000, 0)
    
    async def simulate_loop(self):
        """模擬數據更新迴圈 (1Hz)"""
        while self._running:
            if self.config.get('enabled', True):
                pressure = self.config.get('pressure', 0.0)
                
                # 根據規格: 讀取值需乘以 0.1 得到實際壓力值
                # 所以模擬器需要: 實際值 ÷ 0.1 = 實際值 × 10
                if self.is_vacuum:
                    # 真空: 範圍 0 ~ -100 kPa
                    # 注意: 負數使用補碼，但 Unsigned Int16 無法直接表示負數
                    # 實際設備可能使用有符號數的補碼表示
                    # 例如: -50 kPa = 0xFFCE (65486 dec, 作為有符號數為 -50)
                    pressure_raw = int(pressure * 10)
                    if pressure_raw < 0:
                        # 轉換為無符號 16 位元（補碼）
                        pressure_raw = pressure_raw & 0xFFFF
                else:
                    # 正壓: 範圍 0 ~ 10 kg/cm²
                    pressure_raw = int(pressure * 10)
                    pressure_raw = max(0, min(100, pressure_raw))  # 0 ~ 100 (對應 0 ~ 10 kg/cm²)
                
                self.update_register(0x1000, pressure_raw)
            
            await asyncio.sleep(1.0)  # 1Hz 更新
    
    def set_pressure(self, value: float):
        """設定壓力值"""
        if self.is_vacuum:
            # 真空: 0 ~ -100 kPa
            self.config['pressure'] = max(-100.0, min(0.0, value))
            logger.debug(f"真空壓力計已更新: {value} kPa")
        else:
            # 正壓: 0 ~ 10 kg/cm²
            self.config['pressure'] = max(0.0, min(10.0, value))
            logger.debug(f"正壓壓力計已更新: {value} kg/cm²")

