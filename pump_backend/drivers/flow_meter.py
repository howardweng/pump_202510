"""流量計驅動 (AFM07 系列數顯氣體質量流量計)"""
from typing import Optional, Dict
from loguru import logger
from .modbus_base import ModbusDevice
from config.modbus_devices import get_device_config


class FlowMeterDriver(ModbusDevice):
    """
    流量計驅動 - AFM07 系列
    
    規格：
    - 寄存器地址: 0x0000 (瞬时流量), 0x0001-0x0002 (累積流量)
    - 數據格式: Unsigned Int16 (瞬时), Unsigned Int32 (累積)
    - 轉換係數: 10 (除法)
    """

    def __init__(self):
        config = get_device_config()["flow_meter"]
        super().__init__(
            port=config["port"],
            baudrate=config["baudrate"],
            parity=config["parity"],
            stopbits=config["stopbits"],
            bytesize=config["bytesize"],
            slave_id=config["slave_id"],
            timeout=config["timeout"]
        )

    async def read_instantaneous_flow(self) -> Optional[float]:
        """
        讀取瞬时流量
        
        Returns:
            瞬时流量 (L/min)，失敗返回 None
        """
        registers = await self.read_holding_registers(0x0000, 1)
        if registers is None or len(registers) == 0:
            return None
        
        # Unsigned Int16，係數 10
        raw_value = registers[0]
        flow = raw_value / 10.0
        
        logger.debug(f"📊 瞬时流量: {flow} L/min (原始值: {raw_value})")
        return flow

    async def read_cumulative_flow(self) -> Optional[float]:
        """
        讀取累積流量
        
        Returns:
            累積流量 (L)，失敗返回 None
        """
        registers = await self.read_holding_registers(0x0001, 2)
        if registers is None or len(registers) < 2:
            return None
        
        # Unsigned Int32 (2 個寄存器，Big-Endian)，係數 10
        raw_value = (registers[0] << 16) | registers[1]
        cumulative = raw_value / 10.0
        
        logger.debug(f"📊 累積流量: {cumulative} L (原始值: {raw_value})")
        return cumulative

    async def read_all(self) -> Optional[Dict[str, float]]:
        """
        讀取所有數據
        
        Returns:
            包含瞬时流量和累積流量的字典，失敗返回 None
        """
        instantaneous = await self.read_instantaneous_flow()
        cumulative = await self.read_cumulative_flow()
        
        if instantaneous is None and cumulative is None:
            return None
        
        return {
            "instantaneous_flow": instantaneous,
            "cumulative_flow": cumulative
        }

