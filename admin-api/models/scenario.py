"""場景數據模型"""
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime


class Scenario(BaseModel):
    """場景模型"""
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    device_configs: Dict[str, Dict[str, Any]]  # device_id -> config
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ScenarioCreate(BaseModel):
    """創建場景模型"""
    name: str
    description: Optional[str] = None
    device_configs: Dict[str, Dict[str, Any]]


class ScenarioUpdate(BaseModel):
    """更新場景模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    device_configs: Optional[Dict[str, Dict[str, Any]]] = None


class ScenarioResponse(BaseModel):
    """場景響應模型"""
    success: bool
    scenario: Optional[Scenario] = None
    message: Optional[str] = None


class ScenarioListResponse(BaseModel):
    """場景列表響應模型"""
    success: bool
    scenarios: List[Scenario]
    total: int

