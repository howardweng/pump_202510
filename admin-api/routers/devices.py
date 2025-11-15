"""設備管理 API 路由"""
from fastapi import APIRouter, HTTPException
from typing import List
from models.device import Device, DeviceUpdate, DeviceResponse, DeviceStatus
from models.scenario import ScenarioListResponse
import os
from loguru import logger

router = APIRouter(prefix="/api/devices", tags=["devices"])

# 設備配置（從環境變數或配置文件讀取）
DEVICES = {
    "flow_meter": {
        "id": "flow_meter",
        "name": "流量計",
        "type": "flow_meter",
        "slave_id": 1,
        "port": 5020,
        "status": DeviceStatus.ENABLED,
        "enabled": True,
        "config": {
            "instantaneous_flow": 0.0,
            "cumulative_flow": 0.0
        }
    },
    "dc_meter": {
        "id": "dc_meter",
        "name": "DC 電表",
        "type": "single_phase_power_meter",
        "slave_id": 1,
        "port": 5021,
        "status": DeviceStatus.ENABLED,
        "enabled": True,
        "config": {
            "voltage": 0.0,
            "current": 0.0,
            "active_power": 0.0,
            "reactive_power": 0.0
        }
    },
    "ac110v_meter": {
        "id": "ac110v_meter",
        "name": "AC110V 電表",
        "type": "single_phase_power_meter",
        "slave_id": 2,
        "port": 5022,
        "status": DeviceStatus.ENABLED,
        "enabled": True,
        "config": {
            "voltage": 110.0,
            "current": 0.0,
            "active_power": 0.0,
            "reactive_power": 0.0
        }
    },
    "ac220v_meter": {
        "id": "ac220v_meter",
        "name": "AC220V 電表",
        "type": "single_phase_power_meter",
        "slave_id": 3,
        "port": 5023,
        "status": DeviceStatus.ENABLED,
        "enabled": True,
        "config": {
            "voltage": 220.0,
            "current": 0.0,
            "active_power": 0.0,
            "reactive_power": 0.0
        }
    },
    "ac220v_3p_meter": {
        "id": "ac220v_3p_meter",
        "name": "AC220V 3P 電表",
        "type": "three_phase_power_meter",
        "slave_id": 4,
        "port": 5024,
        "status": DeviceStatus.ENABLED,
        "enabled": True,
        "config": {
            "voltage_a": 220.0,
            "voltage_b": 220.0,
            "voltage_c": 220.0,
            "current_a": 0.0,
            "current_b": 0.0,
            "current_c": 0.0,
            "current_n": 0.0,
            "power_a": 0.0,
            "power_b": 0.0,
            "power_c": 0.0,
            "power_total": 0.0
        }
    },
    "pressure_positive": {
        "id": "pressure_positive",
        "name": "壓力計 (正壓)",
        "type": "pressure_sensor",
        "slave_id": 2,
        "port": 5025,
        "status": DeviceStatus.ENABLED,
        "enabled": True,
        "config": {
            "pressure": 0.0
        }
    },
    "pressure_vacuum": {
        "id": "pressure_vacuum",
        "name": "壓力計 (真空)",
        "type": "pressure_sensor",
        "slave_id": 3,
        "port": 5026,
        "status": DeviceStatus.ENABLED,
        "enabled": True,
        "config": {
            "pressure": 0.0
        }
    },
    "relay_io": {
        "id": "relay_io",
        "name": "繼電器 IO 模組",
        "type": "relay_io",
        "slave_id": 1,
        "port": 5027,
        "status": DeviceStatus.ENABLED,
        "enabled": True,
        "config": {
            "relay_states": [False] * 8,
            "digital_inputs": 0x02
        }
    }
}


@router.get("/", response_model=List[Device])
async def get_all_devices():
    """獲取所有設備狀態"""
    try:
        devices = [Device(**device_data) for device_data in DEVICES.values()]
        return devices
    except Exception as e:
        logger.error(f"獲取設備列表失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}", response_model=Device)
async def get_device(device_id: str):
    """獲取單一設備狀態"""
    if device_id not in DEVICES:
        raise HTTPException(status_code=404, detail=f"設備 {device_id} 不存在")
    
    try:
        return Device(**DEVICES[device_id])
    except Exception as e:
        logger.error(f"獲取設備 {device_id} 失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(device_id: str, update: DeviceUpdate):
    """更新設備模擬數據"""
    if device_id not in DEVICES:
        raise HTTPException(status_code=404, detail=f"設備 {device_id} 不存在")
    
    try:
        device_data = DEVICES[device_id]
        
        # 更新 enabled 狀態
        if update.enabled is not None:
            device_data["enabled"] = update.enabled
            device_data["status"] = DeviceStatus.ENABLED if update.enabled else DeviceStatus.DISABLED
        
        # 更新配置
        if update.config is not None:
            device_data["config"].update(update.config)
        
        # TODO: 發送更新到模擬器服務（通過 MQTT 或直接 API 調用）
        # 這裡暫時只更新本地配置
        
        logger.info(f"設備 {device_id} 已更新: enabled={device_data['enabled']}, config={update.config}")
        
        return DeviceResponse(
            success=True,
            device=Device(**device_data),
            message="設備已更新"
        )
    except Exception as e:
        logger.error(f"更新設備 {device_id} 失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

