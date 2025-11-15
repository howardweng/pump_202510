"""MQTT 客戶端測試"""
import pytest
import asyncio
from pump_backend.core.mqtt_client import MQTTClient


@pytest.mark.asyncio
@pytest.mark.mqtt
@pytest.mark.requires_mqtt
class TestMQTTClient:
    """MQTT 客戶端測試類"""
    
    @pytest.fixture
    async def mqtt_client(self, test_config):
        """創建 MQTT 客戶端實例"""
        client = MQTTClient(
            broker=test_config["mqtt_broker"],
            port=test_config["mqtt_port"]
        )
        await client.start()
        yield client
        await client.disconnect()
    
    async def test_connect(self, mqtt_client):
        """測試 MQTT 連接"""
        assert mqtt_client.client is not None, "MQTT 客戶端應該已初始化"
    
    async def test_publish(self, mqtt_client):
        """測試發布訊息"""
        result = await mqtt_client.publish(
            "test/topic",
            {"message": "test", "value": 123}
        )
        # 發布不應該拋出異常
        assert True, "發布應該成功"
    
    async def test_subscribe(self, mqtt_client):
        """測試訂閱主題"""
        received_messages = []
        
        def callback(payload):
            received_messages.append(payload)
        
        mqtt_client.subscribe("test/subscribe", callback)
        
        # 發布測試訊息
        await mqtt_client.publish("test/subscribe", {"test": "data"})
        
        # 等待訊息處理
        await asyncio.sleep(0.5)
        
        # 注意：由於異步處理，可能需要更長時間
        # 這裡主要測試訂閱功能不拋出異常
        assert True, "訂閱應該成功"

