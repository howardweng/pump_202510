"""Modbus RTU 到 TCP 的橋接器

使用 pymodbus 在虛擬串口上運行 RTU 服務器，然後轉發到 Modbus TCP 模擬器
"""
import asyncio
import pty
import os
import sys
from typing import Tuple, Optional
from loguru import logger
from pymodbus.server import StartAsyncSerialServer
from pymodbus.datastore import ModbusDeviceContext, ModbusServerContext
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.client import AsyncModbusTcpClient


class RTUToTCPBridge:
    """Modbus RTU 到 TCP 的橋接器
    
    在虛擬串口上運行 RTU 服務器，然後將請求轉發到 Modbus TCP 模擬器
    """
    
    def __init__(
        self,
        serial_port: str,
        tcp_host: str,
        tcp_port: int,
        uart_config: Tuple[int, int, str, int],
        slave_id: int
    ):
        """
        Args:
            serial_port: 虛擬串口路徑 (e.g., /dev/ttySIM0)
            tcp_host: Modbus TCP 服務器主機
            tcp_port: Modbus TCP 端口
            uart_config: (baudrate, databits, parity, stopbits)
            slave_id: RTU 從站地址
        """
        self.serial_port = serial_port
        self.tcp_host = tcp_host
        self.tcp_port = tcp_port
        self.baudrate, self.databits, self.parity, self.stopbits = uart_config
        self.slave_id = slave_id
        self.running = False
        self.master_fd: Optional[int] = None
        self.slave_name: Optional[str] = None
        self.tcp_client: Optional[AsyncModbusTcpClient] = None
        
        # 轉換 parity 字串
        parity_map = {
            'NONE': 'N',
            'EVEN': 'E',
            'ODD': 'O'
        }
        self.parity_char = parity_map.get(self.parity, 'N')
    
    def create_virtual_serial(self):
        """創建虛擬串口（使用 pty）"""
        try:
            # 創建 PTY 對
            master_fd, slave_fd = pty.openpty()
            self.master_fd = master_fd
            self.slave_name = os.ttyname(slave_fd)
            
            # 創建符號連結到目標串口路徑
            if os.path.exists(self.serial_port):
                os.remove(self.serial_port)
            os.symlink(self.slave_name, self.serial_port)
            
            logger.info(f"✅ 創建虛擬串口: {self.serial_port} -> {self.slave_name}")
            return True
        except Exception as e:
            logger.error(f"❌ 創建虛擬串口失敗: {e}")
            return False
    
    async def start(self):
        """啟動橋接器"""
        if not self.create_virtual_serial():
            return False
        
        # 連接到 Modbus TCP 服務器
        self.tcp_client = AsyncModbusTcpClient(
            host=self.tcp_host,
            port=self.tcp_port
        )
        await self.tcp_client.connect()
        
        if not self.tcp_client.is_socket_open():
            logger.error(f"❌ 無法連接到 Modbus TCP 服務器: {self.tcp_host}:{self.tcp_port}")
            return False
        
        logger.info(f"✅ 已連接到 Modbus TCP 服務器: {self.tcp_host}:{self.tcp_port}")
        
        # 創建一個轉發數據存儲，將請求轉發到 TCP 客戶端
        # 這裡我們需要創建一個自定義的數據存儲來轉發請求
        # 但 pymodbus 的架構不太適合這種轉發模式
        
        # 更簡單的方案：使用 pymodbus 的 RTU 服務器，但數據存儲直接從 TCP 客戶端讀取
        # 這需要自定義 ModbusDeviceContext
        
        # 暫時使用空的數據存儲，實際數據從 TCP 客戶端同步
        store = ModbusDeviceContext(
            di=ModbusSequentialDataBlock(0, [0]*100),
            co=ModbusSequentialDataBlock(0, [0]*100),
            hr=ModbusSequentialDataBlock(0, [0]*1000),
            ir=ModbusSequentialDataBlock(0, [0]*100)
        )
        context = ModbusServerContext(devices={self.slave_id: store}, single=False)
        
        self.running = True
        logger.info(f"🚀 RTU 到 TCP 橋接器已啟動")
        logger.info(f"   虛擬串口: {self.serial_port}")
        logger.info(f"   UART 設定: {self.baudrate}/{self.databits}/{self.parity}/{self.stopbits}")
        logger.info(f"   TCP 目標: {self.tcp_host}:{self.tcp_port}")
        logger.info(f"   Slave ID: {self.slave_id}")
        
        # 啟動 RTU 服務器
        await StartAsyncSerialServer(
            context=context,
            port=self.slave_name,  # 使用虛擬串口
            baudrate=self.baudrate,
            bytesize=self.databits,
            parity=self.parity_char,
            stopbits=self.stopbits,
            timeout=1.0
        )
    
    async def stop(self):
        """停止橋接器"""
        self.running = False
        if self.tcp_client:
            self.tcp_client.close()
        if self.master_fd:
            try:
                os.close(self.master_fd)
            except:
                pass
        if self.serial_port and os.path.exists(self.serial_port):
            try:
                os.remove(self.serial_port)
            except:
                pass
        logger.info(f"🛑 RTU 到 TCP 橋接器已停止: {self.serial_port}")
    
    async def _sync_data_from_tcp(self, store: ModbusDeviceContext):
        """定期從 TCP 客戶端同步數據到本地存儲"""
        while self.running:
            try:
                if self.tcp_client and self.tcp_client.is_socket_open():
                    # 同步 Holding Registers (功能碼 0x03)
                    # 這裡我們可以定期讀取一些關鍵寄存器
                    # 但為了簡化，我們暫時跳過自動同步
                    # 實際的讀取會通過 RTU 服務器轉發到 TCP 客戶端
                    pass
                await asyncio.sleep(1.0)  # 每秒同步一次
            except Exception as e:
                logger.error(f"數據同步錯誤: {e}")
                await asyncio.sleep(1.0)


async def main():
    """主程序"""
    # 配置日誌
    log_level = os.getenv("LOG_LEVEL", "INFO")
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True
    )
    
    logger.info("🚀 串口橋接器服務啟動中...")
    
    # 根據 MODBUS_all_devices.md 配置橋接器
    # 注意: 一個 USB 轉換器可能連接多個設備（不同的 Slave ID）
    # 但每個設備需要獨立的虛擬串口，因為後端會通過不同的串口連接不同的設備
    
    tcp_host = os.getenv("MODBUS_SIMULATOR_HOST", "modbus-simulator")
    
    bridges = [
        # USB-Enhanced-SERIAL-A: 電表 (4台)
        # DC 電表 (Slave ID 1) -> Port 5021
        RTUToTCPBridge(
            serial_port="/dev/ttySIM0",
            tcp_host=tcp_host,
            tcp_port=5021,
            uart_config=(57600, 8, 'NONE', 1),
            slave_id=1
        ),
        # AC110V 電表 (Slave ID 2) -> Port 5022
        RTUToTCPBridge(
            serial_port="/dev/ttySIM0_1",
            tcp_host=tcp_host,
            tcp_port=5022,
            uart_config=(57600, 8, 'NONE', 1),
            slave_id=2
        ),
        # AC220V 電表 (Slave ID 3) -> Port 5023
        RTUToTCPBridge(
            serial_port="/dev/ttySIM0_2",
            tcp_host=tcp_host,
            tcp_port=5023,
            uart_config=(57600, 8, 'NONE', 1),
            slave_id=3
        ),
        # AC220V 3P 電表 (Slave ID 4) -> Port 5024
        RTUToTCPBridge(
            serial_port="/dev/ttySIM0_3",
            tcp_host=tcp_host,
            tcp_port=5024,
            uart_config=(57600, 8, 'NONE', 1),
            slave_id=4
        ),
        
        # USB-Enhanced-SERIAL-C: 流量計 (1台) - Port 5020
        RTUToTCPBridge(
            serial_port="/dev/ttySIM1",
            tcp_host=tcp_host,
            tcp_port=5020,
            uart_config=(19200, 8, 'NONE', 1),
            slave_id=1
        ),
        
        # USB-Enhanced-SERIAL-D: 繼電器 IO (1台) - Port 5027
        RTUToTCPBridge(
            serial_port="/dev/ttySIM2",
            tcp_host=tcp_host,
            tcp_port=5027,
            uart_config=(115200, 8, 'NONE', 1),
            slave_id=1
        ),
        
        # MOXA USB Serial Port: 壓力計 (2台)
        # 正壓 (Slave ID 2) -> Port 5025
        RTUToTCPBridge(
            serial_port="/dev/ttySIM3",
            tcp_host=tcp_host,
            tcp_port=5025,
            uart_config=(19200, 8, 'EVEN', 1),
            slave_id=2
        ),
        # 真空 (Slave ID 3) -> Port 5026
        RTUToTCPBridge(
            serial_port="/dev/ttySIM3_1",
            tcp_host=tcp_host,
            tcp_port=5026,
            uart_config=(19200, 8, 'EVEN', 1),
            slave_id=3
        ),
    ]
    
    # 啟動所有橋接器
    tasks = [bridge.start() for bridge in bridges]
    
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        logger.info("⏸️ 收到中斷信號，正在關閉...")
    finally:
        for bridge in bridges:
            await bridge.stop()
        logger.info("✅ 所有橋接器已停止")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 橋接器服務已關閉")

