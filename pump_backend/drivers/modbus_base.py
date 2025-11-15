"""MODBUS RTU/TCP 設備基礎類別"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from pymodbus.client import ModbusSerialClient, AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException
from loguru import logger
from typing import Optional, List
from tenacity import retry, stop_after_attempt, wait_fixed
from pump_backend.models.device_health import DeviceStatus, DeviceHealth
from config.settings import settings


class ModbusDevice:
    """
    MODBUS RTU/TCP 設備基礎類別

    v2.0 更新:
    - 使用 ThreadPoolExecutor 執行同步 MODBUS 操作
    - 新增自動重試機制 (tenacity)
    - 新增設備健康監控

    v2.1 更新:
    - 整合設備健康狀態模型
    - 新增上下文管理器支援
    - 完善錯誤處理和狀態更新

    v2.2 更新:
    - 新增 Modbus TCP 支援
    - 自動檢測連接類型（串口或 TCP）
    """

    def __init__(
        self,
        port: str,
        baudrate: int = 9600,
        parity: str = 'N',
        stopbits: int = 1,
        bytesize: int = 8,
        slave_id: int = 1,
        timeout: float = 1.0,
        use_tcp: bool = False,
        tcp_port: int = 502
    ):
        """
        Args:
            port: 串口路徑 (如 "/dev/ttyUSB0") 或 TCP 主機 (如 "localhost")
            baudrate: 波特率（僅用於串口）
            parity: 奇偶校驗（僅用於串口）
            stopbits: 停止位（僅用於串口）
            bytesize: 數據位（僅用於串口）
            slave_id: 從站地址
            timeout: 超時時間
            use_tcp: 是否使用 TCP 連接
            tcp_port: TCP 端口（僅用於 TCP）
        """
        self.port = port
        self.slave_id = slave_id
        self.use_tcp = use_tcp
        self.tcp_port = tcp_port

        if use_tcp:
            # 使用 Modbus TCP
            self.client = AsyncModbusTcpClient(
                host=port,
                port=tcp_port,
                timeout=timeout
            )
            self._executor = None  # TCP 客戶端是異步的，不需要執行緒池
        else:
            # 使用 Modbus RTU (串口)
            self.client = ModbusSerialClient(
                port=port,
                baudrate=baudrate,
                parity=parity,
                stopbits=stopbits,
                bytesize=bytesize,
                timeout=timeout
            )
            self._executor = ThreadPoolExecutor(
                max_workers=1,
                thread_name_prefix=f"Modbus-{port}"
            )

        self.connected = False
        self.status = DeviceStatus()
        self.max_errors = 5  # 連續 5 次失敗視為不健康

    async def connect(self) -> bool:
        """建立連線"""
        try:
            if self.use_tcp:
                # TCP 連接（異步）
                await self.client.connect()
                if hasattr(self.client, 'connected') and self.client.connected:
                    self.connected = True
                    # 連接成功後更新健康狀態
                    self.status.update_success()
                    logger.info(
                        f"✅ MODBUS TCP 已連線: {self.port}:{self.tcp_port} "
                        f"(Slave ID: {self.slave_id})"
                    )
                    return True
                else:
                    logger.error(f"❌ MODBUS TCP 連線失敗: {self.port}:{self.tcp_port}")
                    return False
            else:
                # 串口連接（同步，需要在執行緒池中執行）
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self._executor,
                    self._connect_sync
                )
                return result
        except Exception as e:
            logger.exception(f"❌ MODBUS 連線異常: {e}")
            return False

    def _connect_sync(self) -> bool:
        """同步連接（用於串口）"""
        try:
            if self.client.connect():
                self.connected = True
                # 連接成功後更新健康狀態
                self.status.update_success()
                logger.info(
                    f"✅ MODBUS RTU 已連線: {self.port} "
                    f"(Slave ID: {self.slave_id})"
                )
                return True
            else:
                logger.error(f"❌ MODBUS RTU 連線失敗: {self.port}")
                return False
        except Exception as e:
            logger.exception(f"❌ MODBUS RTU 連線異常: {e}")
            return False

    async def read_holding_registers(
        self,
        address: int,
        count: int
    ) -> Optional[List[int]]:
        """
        讀取保持寄存器 (非同步)
        """
        try:
            if self.use_tcp:
                # TCP 讀取（異步）
                # 注意：pymodbus 3.11+ 使用 device_id 參數
                result = await self.client.read_holding_registers(
                    address=address,
                    count=count,
                    device_id=self.slave_id
                )
            else:
                # 串口讀取（同步，在執行緒池中執行）
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self._executor,
                    self._read_holding_registers_sync,
                    address,
                    count
                )

            if result.isError():
                raise ModbusException(
                    f"讀取錯誤 [Slave={self.slave_id}, "
                    f"Addr={address}, Count={count}]"
                )

            self.status.update_success()
            if self.status.health == DeviceHealth.HEALTHY:
                logger.debug(f"✅ MODBUS 讀取成功 [{self.port}]")

            return result.registers

        except Exception as e:
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
    ) -> object:
        """
        讀取保持寄存器 (同步版本，在執行緒池中執行)
        """
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

        return result

    async def write_single_coil(
        self,
        address: int,
        value: bool
    ) -> bool:
        """
        寫入單個線圈 (非同步)
        """
        try:
            if self.use_tcp:
                # TCP 寫入（異步）
                # 注意：pymodbus 3.11+ 使用 device_id 參數
                result = await self.client.write_coil(
                    address=address,
                    value=value,
                    device_id=self.slave_id
                )
            else:
                # 串口寫入（同步，在執行緒池中執行）
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self._executor,
                    self._write_single_coil_sync,
                    address,
                    value
                )

            if result.isError():
                raise ModbusException(f"寫入失敗 [Addr={address}]")

            return True
        except Exception as e:
            logger.error(f"❌ MODBUS 寫入失敗 [{self.port}]: {e}")
            return False

    def _write_single_coil_sync(self, address: int, value: bool) -> object:
        """寫入單個線圈 (同步)"""
        result = self.client.write_coil(
            address=address,
            value=value,
            slave=self.slave_id
        )

        if result.isError():
            raise ModbusException(f"寫入失敗 [Addr={address}]")

        return result

    async def read_discrete_inputs(
        self,
        address: int,
        count: int
    ) -> Optional[List[bool]]:
        """
        讀取離散輸入 (非同步)
        """
        try:
            if self.use_tcp:
                # TCP 讀取（異步）
                # 注意：pymodbus 3.11+ 使用 device_id 參數
                result = await self.client.read_discrete_inputs(
                    address=address,
                    count=count,
                    device_id=self.slave_id
                )
            else:
                # 串口讀取（同步，在執行緒池中執行）
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self._executor,
                    self._read_discrete_inputs_sync,
                    address,
                    count
                )

            if result.isError():
                raise ModbusException(
                    f"讀取離散輸入錯誤 [Slave={self.slave_id}, "
                    f"Addr={address}, Count={count}]"
                )

            return result.bits

        except Exception as e:
            logger.error(f"❌ MODBUS 讀取離散輸入失敗 [{self.port}]: {e}")
            return None

    def _read_discrete_inputs_sync(
        self,
        address: int,
        count: int
    ) -> object:
        """讀取離散輸入 (同步)"""
        result = self.client.read_discrete_inputs(
            address=address,
            count=count,
            slave=self.slave_id
        )

        if result.isError():
            raise ModbusException(
                f"讀取離散輸入錯誤 [Slave={self.slave_id}, "
                f"Addr={address}, Count={count}]"
            )

        return result

    async def disconnect_async(self):
        """斷線（異步版本）"""
        if self.connected:
            if self.use_tcp:
                # TCP 斷線（異步）
                try:
                    await self.client.close()
                except:
                    pass
            else:
                # 串口斷線（同步）
                self.client.close()
            
            self.connected = False
            self.status.health = DeviceHealth.OFFLINE
            logger.info(f"🔌 MODBUS 已斷線: {self.port}")

        # 關閉執行緒池（僅串口）
        if self._executor:
            self._executor.shutdown(wait=True)

    def disconnect(self):
        """斷線（同步版本，向後兼容）"""
        if self.connected:
            if self.use_tcp:
                # TCP 斷線（嘗試同步關閉）
                try:
                    # 如果事件循環正在運行，使用 run_coroutine_threadsafe
                    loop = None
                    try:
                        loop = asyncio.get_running_loop()
                    except RuntimeError:
                        pass
                    
                    if loop:
                        # 在運行中的事件循環中執行
                        import asyncio
                        asyncio.create_task(self.client.close())
                    else:
                        # 創建新的事件循環
                        asyncio.run(self.client.close())
                except:
                    pass
            else:
                # 串口斷線
                self.client.close()
            
            self.connected = False
            self.status.health = DeviceHealth.OFFLINE
            logger.info(f"🔌 MODBUS 已斷線: {self.port}")

        # 關閉執行緒池（僅串口）
        if self._executor:
            self._executor.shutdown(wait=True)

    async def __aenter__(self):
        """非同步上下文管理器入口"""
        if not self.connected:
            await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """非同步上下文管理器出口"""
        self.disconnect()

    @asynccontextmanager
    async def connection(self):
        """上下文管理器，確保資源正確釋放"""
        try:
            if not self.connected:
                await self.connect()
            yield self
        finally:
            # 不自動斷線，由外部管理生命週期
            pass

    def __del__(self):
        """析構函數"""
        self.disconnect()
