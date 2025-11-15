"""MQTT 訊息節流發布器"""
import asyncio
import time
from typing import Dict, Optional
from loguru import logger
from core.mqtt_client import MQTTClient


class ThrottledPublisher:
    """
    MQTT 訊息節流發布器

    只在間隔時間足夠時發布訊息，避免過度發布
    適用於高頻率感測器數據
    """

    def __init__(self, mqtt_client: MQTTClient, min_interval: float = 0.1):
        """
        Args:
            mqtt_client: MQTT 客戶端
            min_interval: 最小發布間隔（秒），預設 100ms
        """
        self.mqtt = mqtt_client
        self.min_interval = min_interval
        self.last_publish_time: Dict[str, float] = {}
        self._pending_payloads: Dict[str, dict] = {}  # 待發布的訊息

    async def publish_if_needed(self, topic: str, payload: dict):
        """
        只在間隔時間足夠時發布訊息

        Args:
            topic: MQTT 主題
            payload: 訊息內容
        """
        now = time.time()
        last_time = self.last_publish_time.get(topic, 0)

        if now - last_time >= self.min_interval:
            # 可以發布
            await self.mqtt.publish(topic, payload)
            self.last_publish_time[topic] = now
            # 清除待發布的訊息
            self._pending_payloads.pop(topic, None)
        else:
            # 節流：保存最新的訊息，稍後發布
            self._pending_payloads[topic] = payload

    async def flush_pending(self):
        """發布所有待發布的訊息"""
        if not self._pending_payloads:
            return

        now = time.time()
        topics_to_publish = []

        for topic, payload in self._pending_payloads.items():
            last_time = self.last_publish_time.get(topic, 0)
            if now - last_time >= self.min_interval:
                topics_to_publish.append((topic, payload))

        for topic, payload in topics_to_publish:
            await self.mqtt.publish(topic, payload)
            self.last_publish_time[topic] = time.time()
            del self._pending_payloads[topic]

    async def force_publish(self, topic: str, payload: dict):
        """強制發布訊息（忽略節流）"""
        await self.mqtt.publish(topic, payload)
        self.last_publish_time[topic] = time.time()
        self._pending_payloads.pop(topic, None)

