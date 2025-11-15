"""繼電器 IO 驅動 (Waveshare Modbus RTU Relay)"""
import asyncio
from typing import Optional, Dict
from loguru import logger
from .modbus_base import ModbusDevice
from config.modbus_devices import get_device_config


class RelayIODriver(ModbusDevice):
    """
    繼電器 IO 驅動
    
    功能：
    - 控制 8 個繼電器通道（CH1-CH8）
    - 讀取數位輸入（緊急停止、測試蓋狀態）
    - 支援功能碼 0x05 (Write Single Coil) 和 0x0F (Write Multiple Coils)
    - 支援功能碼 0x02 (Read Discrete Inputs)
    """

    def __init__(self):
        config = get_device_config()["relay_io"]
        super().__init__(
            port=config["port"],
            baudrate=config["baudrate"],
            parity=config["parity"],
            stopbits=config["stopbits"],
            bytesize=config["bytesize"],
            slave_id=config["slave_id"],
            timeout=config["timeout"]
        )
        
        # 繼電器通道映射（CH1-CH8 對應 Coil 0x0000-0x0007）
        self.relay_channels = {
            'CH1': 0x0000,  # 電磁閥 A
            'CH2': 0x0001,  # 電磁閥 B
            'CH3': 0x0002,  # 電磁閥 C
            'CH4': 0x0003,  # 電磁閥 D
            'CH5': 0x0004,  # DC 電源
            'CH6': 0x0005,  # AC110V 電源
            'CH7': 0x0006,  # AC220V 電源
            'CH8': 0x0007,  # AC220V 3P 電源
        }

    async def set_relay(self, channel: int, state: bool) -> bool:
        """
        設定單個繼電器狀態
        
        Args:
            channel: 繼電器通道 (1-8)
            state: True=開啟, False=關閉
            
        Returns:
            是否成功
        """
        if channel < 1 or channel > 8:
            logger.error(f"❌ 無效的繼電器通道: {channel} (應為 1-8)")
            return False
        
        address = channel - 1  # Coil 地址從 0 開始
        return await self.write_single_coil(address, state)

    async def set_relays(self, states: Dict[int, bool]) -> bool:
        """
        設定多個繼電器狀態
        
        Args:
            states: 字典 {channel: state}，例如 {1: True, 2: False}
            
        Returns:
            是否成功
        """
        try:
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(
                self._executor,
                self._write_multiple_coils_sync,
                states
            )
            if success:
                self.status.update_success()
            return success
        except Exception as e:
            self.status.update_error()
            logger.error(f"❌ 設定多個繼電器失敗: {e}")
            return False

    def _write_multiple_coils_sync(self, states: Dict[int, bool]) -> bool:
        """寫入多個線圈（同步）"""
        if not self.connected:
            if not self.connect():
                raise Exception("設備未連線")
        
        # 轉換為地址列表和值列表
        addresses = []
        values = []
        for channel, state in sorted(states.items()):
            if 1 <= channel <= 8:
                addresses.append(channel - 1)
                values.append(state)
        
        if not addresses:
            return False
        
        # 使用功能碼 0x0F (Write Multiple Coils)
        result = self.client.write_coils(
            address=addresses[0],
            values=values,
            slave=self.slave_id
        )
        
        if result.isError():
            raise Exception(f"寫入多個繼電器失敗: {result}")
        
        return True

    async def all_relays_off(self) -> bool:
        """
        關閉所有繼電器
        
        Returns:
            是否成功
        """
        states = {i: False for i in range(1, 9)}
        return await self.set_relays(states)

    async def read_digital_inputs(self) -> Optional[int]:
        """
        讀取數位輸入
        
        Returns:
            8 位元整數，Bit0=緊急停止, Bit1=測試蓋狀態
            None 表示讀取失敗
        """
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self._executor,
                self._read_discrete_inputs_sync
            )
            if result is not None:
                self.status.update_success()
            return result
        except Exception as e:
            self.status.update_error()
            logger.error(f"❌ 讀取數位輸入失敗: {e}")
            return None

    def _read_discrete_inputs_sync(self) -> Optional[int]:
        """讀取離散輸入（同步）"""
        if not self.connected:
            if not self.connect():
                return None
        
        # 功能碼 0x02 (Read Discrete Inputs)
        # 讀取 Bit 0-7 (地址 0x0000-0x0007)
        result = self.client.read_discrete_inputs(
            address=0x0000,
            count=8,
            slave=self.slave_id
        )
        
        if result.isError():
            raise Exception(f"讀取數位輸入失敗: {result}")
        
        # 轉換為 8 位元整數
        bits = result.bits[:8]  # 只取前 8 位
        value = sum(bit << i for i, bit in enumerate(bits))
        return value

    def read_digital_inputs_sync(self) -> Optional[int]:
        """
        讀取數位輸入（同步版本，供安全監控器使用）
        
        Returns:
            8 位元整數，Bit0=緊急停止, Bit1=測試蓋狀態
        """
        return self._read_discrete_inputs_sync()

    def all_relays_off_sync(self) -> bool:
        """
        關閉所有繼電器（同步版本，供安全監控器使用）
        
        Returns:
            是否成功
        """
        try:
            if not self.connected:
                if not self.connect():
                    return False
            
            # 使用功能碼 0x0F 寫入 8 個線圈為 False
            result = self.client.write_coils(
                address=0x0000,
                values=[False] * 8,
                slave=self.slave_id
            )
            
            if result.isError():
                logger.error(f"❌ 關閉所有繼電器失敗: {result}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"❌ 關閉所有繼電器異常: {e}")
            return False

    def set_valves_sync(self, A: bool = False, B: bool = False, 
                       C: bool = False, D: bool = False) -> bool:
        """
        設定電磁閥狀態（同步版本，供安全監控器使用）
        
        Args:
            A, B, C, D: 各電磁閥狀態
            
        Returns:
            是否成功
        """
        try:
            if not self.connected:
                if not self.connect():
                    return False
            
            # CH1-CH4 對應電磁閥 A-D
            values = [A, B, C, D] + [False] * 4  # 只設定前 4 個，其他保持關閉
            
            result = self.client.write_coils(
                address=0x0000,
                values=values,
                slave=self.slave_id
            )
            
            if result.isError():
                logger.error(f"❌ 設定電磁閥失敗: {result}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"❌ 設定電磁閥異常: {e}")
            return False

    def power_off_all_sync(self) -> bool:
        """
        切斷所有電源（同步版本，供安全監控器使用）
        
        Returns:
            是否成功
        """
        try:
            if not self.connected:
                if not self.connect():
                    return False
            
            # CH5-CH8 對應電源開關
            values = [False] * 4 + [False] * 4  # 關閉所有電源
            
            result = self.client.write_coils(
                address=0x0004,  # 從 CH5 開始
                values=[False] * 4,
                slave=self.slave_id
            )
            
            if result.isError():
                logger.error(f"❌ 切斷電源失敗: {result}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"❌ 切斷電源異常: {e}")
            return False

