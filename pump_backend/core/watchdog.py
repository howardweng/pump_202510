"""看門狗計時器"""
import asyncio
import time
from loguru import logger
from core.safety_monitor import SafetyMonitor
from core.mqtt_client import MQTTClient
from config.mqtt_topics import SAFETY_ALERT


class Watchdog:
    """
    看門狗計時器

    監控安全監控器執行緒是否正常運作
    如超過閾值未更新，觸發緊急停止

    v2.1 更新: 實作超時緊急處理機制
    """

    def __init__(self, timeout: float = 0.5, mqtt_client: MQTTClient = None):
        """
        Args:
            timeout: 看門狗超時時間 (秒)，預設 500ms
            mqtt_client: MQTT 客戶端（用於發布警報）
        """
        self.timeout = timeout
        self.mqtt = mqtt_client
        self._triggered = False  # 避免重複觸發

    async def monitor(self, safety_monitor: SafetyMonitor):
        """
        監控安全監控器健康狀態

        Args:
            safety_monitor: 安全監控器實例
        """
        logger.info(f"🐕 看門狗已啟動 (超時: {self.timeout}s)")

        while True:
            await asyncio.sleep(0.1)  # 每 100ms 檢查一次

            last_update = safety_monitor.watchdog_last_update
            elapsed = time.time() - last_update

            if elapsed > self.timeout:
                if not self._triggered:
                    self._triggered = True
                    await self._handle_timeout(safety_monitor, elapsed)
            else:
                # 恢復正常，重置觸發標誌
                if self._triggered:
                    self._triggered = False
                    logger.info("✅ 安全監控迴圈已恢復正常")

    async def _handle_timeout(self, safety_monitor: SafetyMonitor, elapsed: float):
        """
        處理看門狗超時

        v2.1 更新: 實作緊急停止機制
        """
        logger.critical(
            f"🚨 安全監控迴圈疑似卡死！"
            f"最後更新: {elapsed:.3f}s 前"
        )

        # 發布 MQTT 警報
        if self.mqtt:
            try:
                await self.mqtt.publish(SAFETY_ALERT, {
                    'type': 'critical',
                    'message': '🚨 安全監控迴圈異常，觸發緊急停止',
                    'elapsed_time': elapsed,
                    'timestamp': time.time()
                })
            except Exception as e:
                logger.error(f"❌ 無法發布看門狗警報: {e}")

        # 觸發緊急停止（如果安全監控器支援）
        try:
            # 嘗試直接調用 IO 驅動進行緊急停止
            # 注意：這是在 asyncio 執行緒中，需要同步操作
            if hasattr(safety_monitor, 'io_driver'):
                logger.critical("🛑 執行緊急停止程序...")
                # 使用 run_in_executor 執行同步緊急停止
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    safety_monitor.io_driver.all_relays_off_sync
                )
                logger.critical("✅ 緊急停止已執行")
        except Exception as e:
            logger.exception(f"❌ 緊急停止執行失敗: {e}")

