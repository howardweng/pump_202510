"""轉發數據存儲 - 將 RTU 請求轉發到 Modbus TCP"""
import asyncio
import threading
from typing import List, Optional
from pymodbus.datastore import ModbusDeviceContext
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.client import AsyncModbusTcpClient
from loguru import logger


class ForwardingModbusContext(ModbusDeviceContext):
    """
    轉發 Modbus 數據存儲
    
    攔截所有讀寫操作，轉發到 Modbus TCP 客戶端
    
    注意: pymodbus 服務器的 getValues/setValues 是同步方法，
    但 TCP 客戶端是異步的，需要使用線程安全的方式調用
    """
    
    def __init__(self, tcp_client: AsyncModbusTcpClient, slave_id: int, event_loop: asyncio.AbstractEventLoop):
        """
        Args:
            tcp_client: Modbus TCP 客戶端
            slave_id: RTU 從站地址
            event_loop: 事件循環（用於運行異步操作）
        """
        # 初始化基礎數據塊（用於緩存）
        # ModbusDeviceContext 接受關鍵字參數
        super().__init__(
            di=ModbusSequentialDataBlock(0, [0]*100),
            co=ModbusSequentialDataBlock(0, [0]*100),
            hr=ModbusSequentialDataBlock(0, [0]*1000),
            ir=ModbusSequentialDataBlock(0, [0]*100)
        )
        self.tcp_client = tcp_client
        self.slave_id = slave_id
        self._event_loop = event_loop
    
    def _run_async(self, coro):
        """在事件循環中運行異步函數（線程安全）"""
        try:
            if self._event_loop.is_running():
                # 如果循環正在運行，使用 run_coroutine_threadsafe
                future = asyncio.run_coroutine_threadsafe(coro, self._event_loop)
                return future.result(timeout=2.0)
            else:
                # 如果循環未運行，直接運行
                return self._event_loop.run_until_complete(coro)
        except Exception as e:
            logger.error(f"異步調用失敗: {e}")
            raise
    
    def getValues(self, fc_as_hex: int, address: int, count: int = 1) -> List[int]:
        """
        讀取值（攔截並轉發到 TCP）
        
        Args:
            fc_as_hex: 功能碼（十六進制）
            address: 起始地址
            count: 讀取數量
        """
        try:
            # 根據功能碼轉換為對應的讀取方法
            if fc_as_hex == 0x01:  # Read Coils
                result = self._run_async(
                    self.tcp_client.read_coils(address, count, slave=self.slave_id)
                )
            elif fc_as_hex == 0x02:  # Read Discrete Inputs
                result = self._run_async(
                    self.tcp_client.read_discrete_inputs(address, count, slave=self.slave_id)
                )
            elif fc_as_hex == 0x03:  # Read Holding Registers
                result = self._run_async(
                    self.tcp_client.read_holding_registers(address, count, slave=self.slave_id)
                )
            elif fc_as_hex == 0x04:  # Read Input Registers
                result = self._run_async(
                    self.tcp_client.read_input_registers(address, count, slave=self.slave_id)
                )
            else:
                logger.warning(f"不支援的功能碼: {fc_as_hex}")
                return [0] * count
            
            if result.isError():
                logger.error(f"TCP 讀取錯誤: {result}")
                # 返回緩存的值
                return super().getValues(fc_as_hex, address, count)
            
            # 提取值
            values = result.bits if hasattr(result, 'bits') else result.registers
            
            # 更新本地緩存（直接調用父類方法，避免遞歸）
            super().setValues(fc_as_hex, address, values)
            
            return values
            
        except Exception as e:
            logger.error(f"轉發讀取請求失敗: {e}")
            # 返回緩存的值
            return super().getValues(fc_as_hex, address, count)
    
    def setValues(self, fc_as_hex: int, address: int, values: List[int]):
        """
        寫入值（攔截並轉發到 TCP）
        
        Args:
            fc_as_hex: 功能碼（十六進制）
            address: 起始地址
            values: 要寫入的值
        """
        try:
            # 更新本地緩存
            super().setValues(fc_as_hex, address, values)
            
            # 根據功能碼轉換為對應的寫入方法
            if fc_as_hex == 0x05:  # Write Single Coil
                value = bool(values[0]) if values else False
                result = self._run_async(
                    self.tcp_client.write_coil(address, value, slave=self.slave_id)
                )
            elif fc_as_hex == 0x06:  # Write Single Register
                value = values[0] if values else 0
                result = self._run_async(
                    self.tcp_client.write_register(address, value, slave=self.slave_id)
                )
            elif fc_as_hex == 0x0F:  # Write Multiple Coils
                result = self._run_async(
                    self.tcp_client.write_coils(address, values, slave=self.slave_id)
                )
            elif fc_as_hex == 0x10:  # Write Multiple Registers
                result = self._run_async(
                    self.tcp_client.write_registers(address, values, slave=self.slave_id)
                )
            else:
                logger.warning(f"不支援的寫入功能碼: {fc_as_hex}")
                return
            
            if result.isError():
                logger.error(f"TCP 寫入錯誤: {result}")
            
        except Exception as e:
            logger.error(f"轉發寫入請求失敗: {e}")

