"""壓力計驅動 (Delta DPA 系列壓力感測器)"""
from typing import Optional, Dict
from loguru import logger
from .modbus_base import ModbusDevice
from config.modbus_devices import get_device_config


class PressureSensorDriver(ModbusDevice):
    """
    壓力計驅動 - Delta DPA 系列
    
    規格：
    - 寄存器地址: 0x1000 (PV 值)
    - 數據格式: Unsigned Int16
    - 轉換係數: 0.1 (乘法)
    - 正壓範圍: 0 ~ 1.0 MPa (0 ~ 10 kg/cm²)
    - 真空範圍: 0 ~ -0.1 MPa (0 ~ -100 kPa)
    """

    def __init__(self, sensor_type: str = "positive"):
        """
        Args:
            sensor_type: "positive" 或 "vacuum"
        """
        config_key = "pressure_positive" if sensor_type == "positive" else "pressure_vacuum"
        config = get_device_config()[config_key]
        
        super().__init__(
            port=config["port"],
            baudrate=config["baudrate"],
            parity=config["parity"],
            stopbits=config["stopbits"],
            bytesize=config["bytesize"],
            slave_id=config["slave_id"],
            timeout=config["timeout"]
        )
        self.sensor_type = sensor_type

    async def read_pressure(self) -> Optional[float]:
        """
        讀取壓力值
        
        Returns:
            壓力值 (MPa)，失敗返回 None
            正壓: 0 ~ 1.0 MPa
            真空: 0 ~ -0.1 MPa
        """
        registers = await self.read_holding_registers(0x1000, 1)
        if registers is None or len(registers) == 0:
            return None
        
        # Unsigned Int16，係數 0.1 (乘法)
        raw_value = registers[0]
        pressure_mpa = raw_value * 0.1
        
        # 真空感測器需要轉換為負值
        if self.sensor_type == "vacuum":
            # 真空感測器: 0 = 0 MPa, 最大值 = -0.1 MPa
            # 假設原始值範圍是 0-1000，對應 0 到 -0.1 MPa
            # 需要根據實際規格調整
            pressure_mpa = -pressure_mpa / 1000.0 if pressure_mpa > 0 else 0.0
        
        logger.debug(
            f"📊 {self.sensor_type} 壓力: {pressure_mpa:.3f} MPa "
            f"(原始值: {raw_value})"
        )
        return pressure_mpa

    async def read_pressure_kgcm2(self) -> Optional[float]:
        """
        讀取壓力值（單位: kg/cm²）
        
        Returns:
            壓力值 (kg/cm²)，失敗返回 None
        """
        pressure_mpa = await self.read_pressure()
        if pressure_mpa is None:
            return None
        
        # 1 MPa = 10.1972 kg/cm²
        pressure_kgcm2 = pressure_mpa * 10.1972
        return pressure_kgcm2

