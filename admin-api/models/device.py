"""設備數據模型"""
from pydantic import BaseModel
from typing import Dict, Any, Optional
from enum import Enum


class DeviceType(str, Enum):
    """設備類型"""
    FLOW_METER = "flow_meter"
    PRESSURE_SENSOR = "pressure_sensor"
    SINGLE_PHASE_POWER_METER = "single_phase_power_meter"
    THREE_PHASE_POWER_METER = "three_phase_power_meter"
    RELAY_IO = "relay_io"


class DeviceStatus(str, Enum):
    """設備狀態"""
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"


class Device(BaseModel):
    """設備模型"""
    id: str
    name: str
    type: DeviceType
    slave_id: int
    port: int
    status: DeviceStatus
    enabled: bool
    config: Dict[str, Any]
    last_update: Optional[str] = None


class DeviceUpdate(BaseModel):
    """設備更新模型"""
    enabled: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None


class DeviceResponse(BaseModel):
    """設備響應模型"""
    success: bool
    device: Optional[Device] = None
    message: Optional[str] = None

