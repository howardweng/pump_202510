"""MODBUS 模擬器基礎類別"""
from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusDeviceContext, ModbusServerContext
from pymodbus.datastore import ModbusSequentialDataBlock
from typing import Dict, Any, Optional
import asyncio
from loguru import logger


class BaseModbusSimulator:
    """MODBUS 模擬器基礎類別"""
    
    def __init__(self, slave_id: int, port: int, config: Dict[str, Any]):
        self.slave_id = slave_id
        self.port = port
        self.config = config
        self.store = ModbusDeviceContext(
            di=ModbusSequentialDataBlock(0, [0]*100),  # Discrete Inputs
            co=ModbusSequentialDataBlock(0, [0]*100),  # Coils
            hr=ModbusSequentialDataBlock(0, [0]*5000), # Holding Registers (支持到 0x1000+)
            ir=ModbusSequentialDataBlock(0, [0]*100)   # Input Registers
        )
        self.context = ModbusServerContext(devices={slave_id: self.store}, single=False)
        self._running = False
        self._server_task: Optional[asyncio.Task] = None
        self._simulate_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """啟動模擬器"""
        self._running = True
        
        # 啟動 MODBUS TCP 服務器（異步）
        self._server_task = asyncio.create_task(
            StartAsyncTcpServer(
                context=self.context,
                address=("0.0.0.0", self.port)
            )
        )
        
        # 啟動模擬數據更新迴圈
        if hasattr(self, 'simulate_loop'):
            self._simulate_task = asyncio.create_task(self.simulate_loop())
        
        logger.info(f"✅ MODBUS 模擬器已啟動 [Slave ID: {self.slave_id}, Port: {self.port}]")
    
    async def stop(self):
        """停止模擬器"""
        self._running = False
        
        if self._simulate_task:
            self._simulate_task.cancel()
            try:
                await self._simulate_task
            except asyncio.CancelledError:
                pass
        
        if self._server_task:
            self._server_task.cancel()
            try:
                await self._server_task
            except asyncio.CancelledError:
                pass
        
        logger.info(f"🛑 MODBUS 模擬器已停止 [Slave ID: {self.slave_id}]")
    
    def update_register(self, address: int, value: int):
        """更新寄存器值 (Holding Registers)"""
        # 確保值在 16 位元範圍內
        value = value & 0xFFFF
        self.store.setValues(3, address, [value])  # 3 = Holding Registers
    
    def get_register(self, address: int) -> int:
        """讀取寄存器值 (Holding Registers)"""
        values = self.store.getValues(3, address, 1)
        return values[0] if values else 0
    
    def update_coil(self, address: int, value: bool):
        """更新線圈值 (Coils) - 使用函數碼 0x05 (Write Single Coil)"""
        self.store.setValues(0x05, address, [value])
    
    def get_coil(self, address: int) -> bool:
        """讀取線圈值 (Coils) - 使用函數碼 0x01 (Read Coils)"""
        values = self.store.getValues(0x01, address, 1)
        return bool(values[0]) if values else False
    
    def update_discrete_input(self, address: int, value: int):
        """更新離散輸入值 (Discrete Inputs) - 使用函數碼 0x02 (Read Discrete Inputs)"""
        # 注意: Discrete Inputs 通常是只讀的，但模擬器中我們需要能夠設置它們
        # 直接操作底層數據塊
        self.store.store['d'].setValues(address, [value])
    
    def get_discrete_input(self, address: int) -> int:
        """讀取離散輸入值 (Discrete Inputs) - 使用函數碼 0x02 (Read Discrete Inputs)"""
        values = self.store.getValues(0x02, address, 1)
        return values[0] if values else 0

