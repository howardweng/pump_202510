"""感測器服務測試"""
import pytest
import os
from pump_backend.services.sensor_service import SensorService
from pump_backend.core.mqtt_client import MQTTClient


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.sensor
@pytest.mark.requires_simulator
@pytest.mark.requires_mqtt
class TestSensorService:
    """感測器服務測試類"""
    
    @pytest.fixture
    async def mqtt_client(self, test_config):
        """創建 MQTT 客戶端"""
        client = MQTTClient(
            broker=test_config["mqtt_broker"],
            port=test_config["mqtt_port"]
        )
        await client.start()
        yield client
        await client.disconnect()
    
    @pytest.fixture
    async def sensor_service(self, mqtt_client):
        """創建感測器服務實例"""
        os.environ["USE_SIMULATOR"] = "true"
        os.environ["MODBUS_SIMULATOR_HOST"] = "localhost"
        
        service = SensorService(mqtt_client)
        yield service
        service.stop()
    
    async def test_start(self, sensor_service):
        """測試啟動感測器服務"""
        result = await sensor_service.start()
        assert result is True, "感測器服務應該能夠啟動"
    
    async def test_poll_flow_meter(self, sensor_service):
        """測試輪詢流量計"""
        await sensor_service.start()
        
        # 執行一次輪詢
        await sensor_service._poll_flow_meter()
        
        # 應該不拋出異常
        assert True, "輪詢流量計應該成功"
    
    async def test_poll_pressure_sensors(self, sensor_service):
        """測試輪詢壓力計"""
        await sensor_service.start()
        
        # 執行一次輪詢
        await sensor_service._poll_pressure_sensors()
        
        # 應該不拋出異常
        assert True, "輪詢壓力計應該成功"
    
    async def test_poll_power_meters(self, sensor_service):
        """測試輪詢電表"""
        await sensor_service.start()
        
        # 執行一次輪詢
        await sensor_service._poll_power_meters()
        
        # 應該不拋出異常
        assert True, "輪詢電表應該成功"



