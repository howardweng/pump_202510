"""安全監控器 - 100Hz 專用執行緒實作"""
import asyncio
import threading
import time
from queue import Queue, Empty
from typing import Optional
from loguru import logger
from drivers.relay_io import RelayIODriver
from core.mqtt_client import MQTTClient
from config.mqtt_topics import SAFETY_STATUS, SAFETY_ALERT


class SafetyMonitor:
    """
    安全監控器 - 100Hz 專用執行緒實作

    v2.0 更新:
    - 使用專用執行緒確保精確的 10ms 循環
    - 使用 Queue 與主執行緒通訊
    - 緊急操作直接在專用執行緒執行，不等待 MQTT
    """

    def __init__(self, mqtt_client: MQTTClient):
        self.mqtt = mqtt_client
        self.io_driver = RelayIODriver()

        # 安全狀態
        self.emergency_stop_active = False
        self.cover_closed = False
        self.system_locked = False

        # 執行緒控制
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._status_queue = Queue(maxsize=100)  # 狀態佇列

        # 看門狗
        self.watchdog_last_update = time.time()

    async def start(self):
        """啟動安全監控"""
        # 1. 連線 IO 驅動（支援 TCP）
        result = await self.io_driver.connect()
        if not result:
            logger.critical("❌ IO 模組連線失敗，安全監控無法啟動！")
            return False

        # 2. 啟動專用執行緒 (100Hz 輪詢)
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop_thread,
            daemon=True,
            name="SafetyMonitor-100Hz"
        )
        self._monitor_thread.start()
        logger.info("🛡️ 安全監控器已啟動 (100Hz 專用執行緒)")

        # 3. 啟動狀態發布任務 (在主 asyncio 循環)
        asyncio.create_task(self._publish_status_loop())

        return True

    def stop(self):
        """停止安全監控執行緒"""
        self._stop_event.set()
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
        self.io_driver.disconnect()
        logger.info("🛑 安全監控器已停止")

    def _monitor_loop_thread(self):
        """
        專用執行緒中的監控迴圈 - 100Hz (10ms)

        ⚠️ 此方法在獨立執行緒中運行，不能直接使用 asyncio
        """
        target_interval = 0.01  # 10ms

        logger.info("✅ IO 模組已連線，開始 100Hz 監控...")

        while not self._stop_event.is_set():
            loop_start = time.perf_counter()

            # 更新看門狗
            self.watchdog_last_update = time.time()

            try:
                # 讀取 IO 狀態 (同步操作)
                io_status = self.io_driver.read_digital_inputs_sync()

                if io_status is None:
                    logger.warning("⚠️ IO 模組讀取失敗，跳過本次循環")
                else:
                    emergency_pressed = bool(io_status & 0x01)  # Bit0
                    cover_closed = bool(io_status & 0x02)       # Bit1

                    # 將狀態放入佇列供 MQTT 發布
                    try:
                        self._status_queue.put_nowait({
                            'emergency_stop': emergency_pressed,
                            'cover_closed': cover_closed,
                            'system_locked': self.system_locked,
                            'timestamp': time.time()
                        })
                    except:
                        pass  # 佇列滿，捨棄舊數據

                    # === 緊急停止處理 (立即執行) ===
                    if emergency_pressed and not self.emergency_stop_active:
                        self._handle_emergency_stop_sync()
                    elif not emergency_pressed and self.emergency_stop_active:
                        self._handle_emergency_release_sync()

                    # === 測試蓋處理 ===
                    if not cover_closed and self.cover_closed:
                        self._handle_cover_opened_sync()
                    elif cover_closed and not self.cover_closed:
                        self._handle_cover_closed_sync()

                    # 更新狀態
                    self.emergency_stop_active = emergency_pressed
                    self.cover_closed = cover_closed

            except Exception as e:
                logger.exception(f"❌ 安全監控異常: {e}")

            # 精確睡眠，補償執行時間
            elapsed = time.perf_counter() - loop_start
            sleep_time = max(0, target_interval - elapsed)

            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                logger.warning(
                    f"⚠️ 安全監控迴圈超時: {elapsed*1000:.2f}ms > 10ms"
                )

    def _handle_emergency_stop_sync(self):
        """
        緊急停止處理 (同步版本，在專用執行緒執行)

        FR-006: 緊急停止程序
        1. 停止馬達供電
        2. 儲氣筒洩壓
        3. 鎖定所有操作
        4. 記錄日誌
        """
        logger.critical("🚨 緊急停止觸發！執行緊急關閉程序...")

        # 1. 立即切斷所有電源 (同步操作)
        self.io_driver.all_relays_off_sync()

        # 2. 開啟洩壓閥 (A+B)
        self.io_driver.set_valves_sync(A=True, B=True, C=False, D=False)

        # 3. 鎖定系統
        self.system_locked = True

        # 4. 記錄到安全日誌
        logger.bind(event="emergency_stop").critical(
            "緊急停止已執行 | 所有電源已切斷 | 洩壓閥已開啟"
        )

    def _handle_emergency_release_sync(self):
        """緊急停止解除 (同步)"""
        logger.info("🔓 緊急停止已解除")
        self.system_locked = False

        logger.bind(event="emergency_release").info("系統已重置")

    def _handle_cover_opened_sync(self):
        """測試蓋開啟處理 (同步)"""
        logger.warning("⚠️ 測試蓋已開啟！暫停測試...")

        # 只切斷馬達電源，不洩壓
        self.io_driver.power_off_all_sync()

        logger.bind(event="cover_opened").warning("馬達已停止")

    def _handle_cover_closed_sync(self):
        """測試蓋關閉 (同步)"""
        logger.info("✅ 測試蓋已關閉")
        logger.bind(event="cover_closed").info("可繼續測試")

    async def _publish_status_loop(self):
        """
        在主 asyncio 循環中處理 MQTT 發布

        從佇列讀取狀態並發布至 MQTT
        """
        while True:
            try:
                # 非阻塞讀取佇列
                status = self._status_queue.get_nowait()

                # 發布至 MQTT (異步操作)
                await self.mqtt.publish(SAFETY_STATUS, status)

                # 如果有緊急事件，也發布警報
                if status.get('emergency_stop'):
                    await self.mqtt.publish(SAFETY_ALERT, {
                        'type': 'emergency',
                        'message': '🚨 緊急停止'
                    })
                elif not status.get('cover_closed'):
                    await self.mqtt.publish(SAFETY_ALERT, {
                        'type': 'warning',
                        'message': '⚠️ 測試蓋開啟'
                    })

            except Empty:
                # 佇列為空，短暫等待
                await asyncio.sleep(0.01)
            except Exception as e:
                logger.error(f"❌ 狀態發布失敗: {e}")
                await asyncio.sleep(0.1)

    def check_start_conditions(self) -> tuple[bool, str]:
        """
        啟動測試前的安全檢查 (FR-006)

        Returns:
            (是否通過, 錯誤訊息)
        """
        if self.emergency_stop_active:
            return False, "❌ 緊急停止鈕已按下，請解除後再試"

        if not self.cover_closed:
            return False, "❌ 測試蓋未關閉，請關閉後再試"

        if self.system_locked:
            return False, "❌ 系統已鎖定，請檢查安全狀態"

        return True, ""

