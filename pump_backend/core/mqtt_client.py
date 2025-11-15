"""非同步 MQTT 客戶端 (基於 aiomqtt)"""
import asyncio
import json
from typing import Callable, Dict, Optional
from aiomqtt import Client, Message
from loguru import logger
from config.settings import settings


class MQTTClient:
    """
    非同步 MQTT 客戶端 (基於 aiomqtt)

    v2.0 更新: 完全非同步實作，解決 paho-mqtt 執行緒問題
    """

    def __init__(
        self,
        broker: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        self.broker = broker or settings.MQTT_BROKER
        self.port = port or settings.MQTT_PORT
        self.username = username or settings.MQTT_USERNAME
        self.password = password or settings.MQTT_PASSWORD

        self.subscriptions: Dict[str, Callable] = {}
        self.client: Optional[Client] = None
        self._message_task: Optional[asyncio.Task] = None
        self._reconnect_interval = 5.0  # 5秒重連

    async def start(self):
        """啟動 MQTT 連線"""
        await self._connect_with_retry()

    async def _connect_with_retry(self):
        """帶重試的連線"""
        while True:
            try:
                self.client = Client(
                    hostname=self.broker,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    timeout=10.0
                )

                await self.client.__aenter__()
                logger.info(f"✅ MQTT 已連線至 {self.broker}:{self.port}")

                # 訂閱所有主題
                if self.subscriptions:
                    topics = list(self.subscriptions.keys())
                    await self.client.subscribe([(t, 1) for t in topics])
                    logger.info(f"📥 已訂閱 {len(topics)} 個主題")

                # 啟動訊息處理任務
                self._message_task = asyncio.create_task(self._message_loop())

                return

            except Exception as e:
                logger.error(f"❌ MQTT 連線失敗: {e}")
                logger.info(f"⏱️ {self._reconnect_interval} 秒後重試...")
                await asyncio.sleep(self._reconnect_interval)

    async def _message_loop(self):
        """訊息處理迴圈"""
        try:
            async for message in self.client.messages:
                await self._handle_message(message)
        except asyncio.CancelledError:
            logger.info("📭 訊息處理迴圈已停止")
        except Exception as e:
            logger.exception(f"❌ 訊息處理異常: {e}")
            # 重新連線
            await self._connect_with_retry()

    async def _handle_message(self, message: Message):
        """處理單一訊息"""
        topic = message.topic.value

        try:
            payload = json.loads(message.payload.decode())

            if topic in self.subscriptions:
                callback = self.subscriptions[topic]

                # 支援同步和非同步回調
                if asyncio.iscoroutinefunction(callback):
                    await callback(payload)
                else:
                    callback(payload)

        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON 解析失敗 [{topic}]: {e}")
        except Exception as e:
            logger.error(f"❌ 訊息處理失敗 [{topic}]: {e}")

    def subscribe(self, topic: str, callback: Callable):
        """
        訂閱主題並註冊回調函數

        Args:
            topic: MQTT 主題
            callback: 回調函數 (可以是同步或非同步)
        """
        self.subscriptions[topic] = callback
        logger.info(f"📥 註冊訂閱: {topic}")

    async def publish(
        self,
        topic: str,
        payload: dict,
        qos: int = 1,
        retain: bool = False
    ):
        """
        發布訊息

        Args:
            topic: MQTT 主題
            payload: 資料 (字典)
            qos: QoS 等級 (0, 1, 2)
            retain: 是否保留訊息
        """
        if not self.client:
            logger.warning(f"⚠️ MQTT 未連線，無法發布 [{topic}]")
            return

        try:
            message = json.dumps(payload, ensure_ascii=False)
            await self.client.publish(
                topic,
                message,
                qos=qos,
                retain=retain
            )
        except Exception as e:
            logger.error(f"❌ MQTT 發布異常 [{topic}]: {e}")

    async def disconnect(self):
        """斷線"""
        if self._message_task:
            self._message_task.cancel()
            try:
                await self._message_task
            except asyncio.CancelledError:
                pass

        if self.client:
            await self.client.__aexit__(None, None, None)

        logger.info("🔌 MQTT 已斷線")

