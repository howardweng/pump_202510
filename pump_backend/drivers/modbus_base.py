"""MODBUS RTU 設備基礎類別"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException
from loguru import logger
from typing import Optional, List
from tenacity import retry, stop_after_attempt, wait_fixed
from models.device_health import DeviceStatus, DeviceHealth


class ModbusDevice:
    """
    MODBUS RTU 設備基礎類別

    v2.0 更新:
    - 使用 ThreadPoolExecutor 執行同步 MODBUS 操作
    - 新增自動重試機制 (tenacity)
    - 新增設備健康監控

    v2.1 更新:
    - 整合設備健康狀態模型
    - 新增上下文管理器支援
    - 完善錯誤處理和狀態更新
    """

    def __init__(
        self,
        port: str,
        baudrate: int,
        parity: str = 'N',
        stopbits: int = 1,
        bytesize: int = 8,
        slave_id: int = 1,
        timeout: float = 1.0
    ):
        self.port = port
        self.slave_id = slave_id

        self.client = ModbusSerialClient(
            port=port,
            baudrate=baudrate,
            parity=parity,
            stopbits=stopbits,
            bytesize=bytesize,
            timeout=timeout
        )

        # 執行緒池（每個設備一個工作執行緒）
        self._executor = ThreadPoolExecutor(
            max_workers=1,
            thread_name_prefix=f"Modbus-{port}"
        )

        self.connected = False
        # 使用設備健康狀態模型
        self.status = DeviceStatus()
        self.max_errors = 5  # 連續 5 次失敗視為不健康

    def connect(self) -> bool:
        """建立連線 (同步)"""
        try:
            if self.client.connect():
                self.connected = True
                self.status.health = DeviceHealth.HEALTHY
                logger.info(
                    f"✅ MODBUS 已連線: {self.port} "
                    f"(Slave ID: {self.slave_id})"
                )
                return True
            else:
                logger.error(f"❌ MODBUS 連線失敗: {self.port}")
                self.status.health = DeviceHealth.OFFLINE
                return False
        except Exception as e:
            logger.exception(f"❌ MODBUS 連線異常: {e}")
            self.status.health = DeviceHealth.OFFLINE
            return False

    async def read_holding_registers(
        self,
        address: int,
        count: int
    ) -> Optional[List[int]]:
        """
        讀取保持寄存器 (非同步包裝)

        使用 run_in_executor 避免阻塞事件循環

        Args:
            address: 寄存器起始地址
            count: 讀取寄存器數量

        Returns:
            寄存器值列表，失敗返回 None
        """
        loop = asyncio.get_event_loop()

        try:
            # 在執行緒池中執行同步操作
            registers = await loop.run_in_executor(
                self._executor,
                self._read_holding_registers_sync,
                address,
                count
            )

            # 更新成功狀態
            self.status.update_success()
            if self.status.health == DeviceHealth.HEALTHY:
                logger.debug(f"✅ MODBUS 讀取成功 [{self.port}]")

            return registers

        except Exception as e:
            # 更新錯誤狀態
            self.status.update_error()
            logger.error(
                f"❌ MODBUS 讀取失敗 [{self.port}] "
                f"(連續錯誤: {self.status.consecutive_errors}/{self.max_errors}): {e}"
            )

            if self.status.health == DeviceHealth.UNHEALTHY:
                logger.critical(
                    f"🚨 設備不健康: {self.port} "
                    f"(連續 {self.status.consecutive_errors} 次失敗, "
                    f"成功率: {self.status.get_success_rate()*100:.1f}%)"
                )

            return None

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0.1))
    def _read_holding_registers_sync(
        self,
        address: int,
        count: int
    ) -> List[int]:
        """
        讀取保持寄存器 (同步版本，在執行緒池中執行)

        使用 tenacity 自動重試
        """
        if not self.connected:
            if not self.connect():
                raise ModbusException("設備未連線")

        result = self.client.read_holding_registers(
            address=address,
            count=count,
            slave=self.slave_id
        )

        if result.isError():
            raise ModbusException(
                f"讀取錯誤 [Slave={self.slave_id}, "
                f"Addr={address}, Count={count}]"
            )

        return result.registers

    async def write_single_coil(
        self,
        address: int,
        value: bool
    ) -> bool:
        """
        寫入單個線圈 (非同步包裝)

        Args:
            address: 線圈地址
            value: True=開啟, False=關閉

        Returns:
            是否成功
        """
        loop = asyncio.get_event_loop()

        try:
            success = await loop.run_in_executor(
                self._executor,
                self._write_single_coil_sync,
                address,
                value
            )
            if success:
                self.status.update_success()
            return success
        except Exception as e:
            self.status.update_error()
            logger.error(f"❌ MODBUS 寫入失敗 [{self.port}]: {e}")
            return False

    def _write_single_coil_sync(self, address: int, value: bool) -> bool:
        """寫入單個線圈 (同步)"""
        if not self.connected:
            if not self.connect():
                raise ModbusException("設備未連線")

        result = self.client.write_coil(
            address=address,
            value=value,
            slave=self.slave_id
        )

        if result.isError():
            raise ModbusException(f"寫入失敗 [Addr={address}]")

        return True

    def disconnect(self):
        """斷線"""
        if self.connected:
            self.client.close()
            self.connected = False
            self.status.health = DeviceHealth.OFFLINE
            logger.info(f"🔌 MODBUS 已斷線: {self.port}")

        # 關閉執行緒池
        self._executor.shutdown(wait=True)

    # 上下文管理器支援
    async def __aenter__(self):
        """非同步上下文管理器入口"""
        if not self.connected:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self._executor, self.connect)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """非同步上下文管理器出口"""
        self.disconnect()

    @asynccontextmanager
    async def connection(self):
        """上下文管理器，確保資源正確釋放"""
        try:
            if not self.connected:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(self._executor, self.connect)
            yield self
        finally:
            # 不自動斷線，由外部管理生命週期
            pass

    def __del__(self):
        """析構函數"""
        self.disconnect()

