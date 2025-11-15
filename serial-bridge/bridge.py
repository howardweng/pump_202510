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
from pymodbus.datastore import ModbusServerContext
from pymodbus.client import AsyncModbusTcpClient
from forwarding_store import ForwardingModbusContext


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
        self.master_port: Optional[str] = None
        self.socat_process: Optional[object] = None
        self.tcp_client: Optional[AsyncModbusTcpClient] = None
        
        # 轉換 parity 字串
        parity_map = {
            'NONE': 'N',
            'EVEN': 'E',
            'ODD': 'O'
        }
        self.parity_char = parity_map.get(self.parity, 'N')
    
    def create_virtual_serial(self):
        """創建虛擬串口（使用 socat 創建更標準的虛擬串口對）"""
        try:
            import subprocess
            import time
            
            # 使用 socat 創建虛擬串口對
            # socat 創建的虛擬串口對更兼容 pymodbus
            master_port = f"/tmp/{os.path.basename(self.serial_port)}_master"
            slave_port = self.serial_port
            
            # 如果串口已存在，先清理
            if os.path.exists(slave_port):
                if os.path.islink(slave_port):
                    os.remove(slave_port)
                elif os.path.exists(slave_port):
                    logger.warning(f"⚠️ {slave_port} 已存在，嘗試刪除...")
                    try:
                        os.remove(slave_port)
                    except:
                        pass
            
            # 啟動 socat 進程創建虛擬串口對
            # PTY,link= 創建一個 pty 並連結到指定路徑
            cmd = [
                "socat",
                "-d", "-d",  # 調試輸出
                f"PTY,link={slave_port},raw,echo=0",
                f"PTY,link={master_port},raw,echo=0"
            ]
            
            try:
                # 啟動 socat 進程（後台運行）
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # 等待一下讓 socat 創建設備
                time.sleep(0.5)
                
                # 檢查進程是否還在運行
                if process.poll() is not None:
                    stdout, stderr = process.communicate()
                    logger.error(f"❌ socat 進程失敗: {stderr.decode()}")
                    return False
                
                self.socat_process = process
                self.master_port = master_port
                self.slave_name = slave_port
                
                # 檢查設備是否創建成功
                if not os.path.exists(slave_port):
                    logger.error(f"❌ 虛擬串口設備未創建: {slave_port}")
                    return False
                
                logger.info(f"✅ 創建虛擬串口: {slave_port} (使用 socat)")
                return True
                
            except FileNotFoundError:
                logger.error("❌ socat 未安裝，請在 Dockerfile 中安裝 socat")
                return False
            except Exception as e:
                logger.error(f"❌ 啟動 socat 失敗: {e}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 創建虛擬串口失敗: {e}")
            import traceback
            logger.debug(traceback.format_exc())
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
        
        # 檢查連接狀態（pymodbus v3.x 使用 connected 屬性）
        if not hasattr(self.tcp_client, 'connected') or not self.tcp_client.connected:
            logger.error(f"❌ 無法連接到 Modbus TCP 服務器: {self.tcp_host}:{self.tcp_port}")
            return False
        
        logger.info(f"✅ 已連接到 Modbus TCP 服務器: {self.tcp_host}:{self.tcp_port}")
        
        # 獲取當前事件循環
        loop = asyncio.get_event_loop()
        
        # 創建轉發數據存儲，攔截所有讀寫操作並轉發到 TCP 客戶端
        store = ForwardingModbusContext(self.tcp_client, self.slave_id, loop)
        context = ModbusServerContext(devices={self.slave_id: store}, single=False)
        
        self.running = True
        logger.info(f"🚀 RTU 到 TCP 橋接器已啟動")
        logger.info(f"   虛擬串口: {self.serial_port}")
        logger.info(f"   UART 設定: {self.baudrate}/{self.databits}/{self.parity}/{self.stopbits}")
        logger.info(f"   TCP 目標: {self.tcp_host}:{self.tcp_port}")
        logger.info(f"   Slave ID: {self.slave_id}")
        
        # 啟動 RTU 服務器
        # 使用 socat 創建的虛擬串口
        try:
            await StartAsyncSerialServer(
                context=context,
                port=self.slave_name,  # 使用虛擬串口路徑
                baudrate=self.baudrate,
                bytesize=self.databits,
                parity=self.parity_char,
                stopbits=self.stopbits,
                timeout=1.0,
                framer='rtu'
            )
        except Exception as e:
            logger.error(f"❌ 啟動 RTU 服務器失敗: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            raise
    
    async def stop(self):
        """停止橋接器"""
        self.running = False
        if self.tcp_client:
            self.tcp_client.close()
        if self.socat_process:
            try:
                self.socat_process.terminate()
                self.socat_process.wait(timeout=2)
            except:
                try:
                    self.socat_process.kill()
                except:
                    pass
        if self.master_fd:
            try:
                os.close(self.master_fd)
            except:
                pass
        # 清理虛擬串口設備
        for port in [self.serial_port, self.master_port]:
            if port and os.path.exists(port):
                try:
                    if os.path.islink(port):
                        os.remove(port)
                except:
                    pass
        logger.info(f"🛑 RTU 到 TCP 橋接器已停止: {self.serial_port}")


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

