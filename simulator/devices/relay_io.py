"""Waveshare Modbus RTU Relay (D) 模擬器"""
from .base import BaseModbusSimulator
import asyncio
from loguru import logger


class RelayIOSimulator(BaseModbusSimulator):
    """Waveshare Modbus RTU Relay (D) 模擬器
    
    根據 MODBUS_all_devices.md:
    - RTU 地址: 1
    - Coils: 0x0000-0x0007 (CH1-CH8)
    - Discrete Inputs: 0x0000 (Bit 0-7)
    - 功能碼: 0x02 (Read Discrete Inputs), 0x05 (Write Single Coil), 0x0F (Write Multiple Coils)
    - 控制值: 0xFF00 = ON, 0x0000 = OFF
    - 輪詢頻率: 100 Hz
    - Bit 0: 緊急停止 (1=按下, 0=未按下)
    - Bit 1: 測試蓋狀態 (1=關蓋, 0=開蓋)
    """
    
    def __init__(self, slave_id: int = 1, port: int = 5027):
        config = {
            'relay_states': [False] * 8,  # CH1-CH8 繼電器狀態
            'digital_inputs': 0x02,  # Bit 0-7: Bit0=緊急停止, Bit1=測試蓋
            'enabled': True
        }
        super().__init__(slave_id, port, config)
        
        # 初始化 Coils (CH1-CH8 全部關閉)
        for i in range(8):
            self.update_coil(i, False)
        
        # 初始化 Discrete Inputs
        # Bit 0: 緊急停止 (0=未按下), Bit 1: 測試蓋 (1=關蓋)
        self.update_discrete_input(0, 0x02)
    
    async def simulate_loop(self):
        """模擬數據更新迴圈 (100Hz = 0.01秒)"""
        while self._running:
            if self.config.get('enabled', True):
                # 更新 Discrete Inputs (Bit 0-7)
                # 根據規格: Bit 0=緊急停止, Bit 1=測試蓋
                digital_inputs = self.config.get('digital_inputs', 0x02)
                self.update_discrete_input(0, digital_inputs)
            
            await asyncio.sleep(0.01)  # 100Hz 更新
    
    def set_emergency_stop(self, pressed: bool):
        """設定緊急停止狀態"""
        inputs = self.config.get('digital_inputs', 0x02)
        if pressed:
            inputs |= 0x01  # Bit 0 = 1
        else:
            inputs &= 0xFE  # Bit 0 = 0
        self.config['digital_inputs'] = inputs
        logger.info(f"緊急停止狀態已更新: {'按下' if pressed else '未按下'}")
    
    def set_cover_closed(self, closed: bool):
        """設定測試蓋狀態"""
        inputs = self.config.get('digital_inputs', 0x02)
        if closed:
            inputs |= 0x02  # Bit 1 = 1
        else:
            inputs &= 0xFD  # Bit 1 = 0
        self.config['digital_inputs'] = inputs
        logger.info(f"測試蓋狀態已更新: {'關閉' if closed else '開啟'}")
    
    def set_relay(self, channel: int, state: bool):
        """設定繼電器狀態 (CH1-CH8)"""
        if 1 <= channel <= 8:
            self.config['relay_states'][channel - 1] = state
            # 更新 Coil (0x0000-0x0007 對應 CH1-CH8)
            self.update_coil(channel - 1, state)
            logger.debug(f"繼電器 CH{channel} 已更新: {'開啟' if state else '關閉'}")
    
    def get_relay_state(self, channel: int) -> bool:
        """獲取繼電器狀態"""
        if 1 <= channel <= 8:
            return self.config['relay_states'][channel - 1]
        return False
    
    def all_relays_off(self):
        """關閉所有繼電器"""
        for i in range(1, 9):
            self.set_relay(i, False)
        logger.info("所有繼電器已關閉")



