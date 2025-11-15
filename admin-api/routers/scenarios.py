"""場景管理 API 路由"""
from fastapi import APIRouter, HTTPException
from typing import List
from models.scenario import (
    Scenario,
    ScenarioCreate,
    ScenarioUpdate,
    ScenarioResponse,
    ScenarioListResponse
)
from datetime import datetime
import asyncpg
import os
from loguru import logger

router = APIRouter(prefix="/api/scenarios", tags=["scenarios"])

# PostgreSQL 連接配置
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "pump_testing")
POSTGRES_USER = os.getenv("POSTGRES_USER", "pump_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "pump_password_change_me")


async def get_db_connection():
    """獲取資料庫連接"""
    return await asyncpg.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )


async def init_db():
    """初始化資料庫表"""
    conn = await get_db_connection()
    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS scenarios (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                description TEXT,
                device_configs JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("✅ 資料庫表已初始化")
    except Exception as e:
        logger.error(f"初始化資料庫失敗: {e}")
    finally:
        await conn.close()


# 注意: 資料庫初始化將在 main.py 中處理


@router.get("/", response_model=ScenarioListResponse)
async def get_all_scenarios():
    """獲取所有場景"""
    conn = await get_db_connection()
    try:
        rows = await conn.fetch("SELECT * FROM scenarios ORDER BY created_at DESC")
        scenarios = [
            Scenario(
                id=row["id"],
                name=row["name"],
                description=row["description"],
                device_configs=row["device_configs"],
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
            for row in rows
        ]
        return ScenarioListResponse(success=True, scenarios=scenarios, total=len(scenarios))
    except Exception as e:
        logger.error(f"獲取場景列表失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()


@router.get("/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(scenario_id: int):
    """獲取單一場景"""
    conn = await get_db_connection()
    try:
        row = await conn.fetchrow("SELECT * FROM scenarios WHERE id = $1", scenario_id)
        if not row:
            raise HTTPException(status_code=404, detail=f"場景 {scenario_id} 不存在")
        
        scenario = Scenario(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            device_configs=row["device_configs"],
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )
        return ScenarioResponse(success=True, scenario=scenario)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取場景 {scenario_id} 失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()


@router.post("/", response_model=ScenarioResponse)
async def create_scenario(scenario: ScenarioCreate):
    """創建場景"""
    conn = await get_db_connection()
    try:
        row = await conn.fetchrow("""
            INSERT INTO scenarios (name, description, device_configs)
            VALUES ($1, $2, $3)
            RETURNING *
        """, scenario.name, scenario.description, scenario.device_configs)
        
        created_scenario = Scenario(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            device_configs=row["device_configs"],
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )
        
        logger.info(f"場景已創建: {scenario.name}")
        return ScenarioResponse(success=True, scenario=created_scenario, message="場景已創建")
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=400, detail=f"場景名稱 '{scenario.name}' 已存在")
    except Exception as e:
        logger.error(f"創建場景失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()


@router.put("/{scenario_id}", response_model=ScenarioResponse)
async def update_scenario(scenario_id: int, update: ScenarioUpdate):
    """更新場景"""
    conn = await get_db_connection()
    try:
        # 檢查場景是否存在
        existing = await conn.fetchrow("SELECT * FROM scenarios WHERE id = $1", scenario_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"場景 {scenario_id} 不存在")
        
        # 構建更新語句
        updates = []
        values = []
        param_index = 1
        
        if update.name is not None:
            updates.append(f"name = ${param_index}")
            values.append(update.name)
            param_index += 1
        
        if update.description is not None:
            updates.append(f"description = ${param_index}")
            values.append(update.description)
            param_index += 1
        
        if update.device_configs is not None:
            updates.append(f"device_configs = ${param_index}")
            values.append(update.device_configs)
            param_index += 1
        
        if not updates:
            raise HTTPException(status_code=400, detail="沒有提供更新內容")
        
        updates.append(f"updated_at = CURRENT_TIMESTAMP")
        values.append(scenario_id)
        
        query = f"UPDATE scenarios SET {', '.join(updates)} WHERE id = ${param_index} RETURNING *"
        row = await conn.fetchrow(query, *values)
        
        updated_scenario = Scenario(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            device_configs=row["device_configs"],
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )
        
        logger.info(f"場景已更新: {scenario_id}")
        return ScenarioResponse(success=True, scenario=updated_scenario, message="場景已更新")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新場景 {scenario_id} 失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()


@router.delete("/{scenario_id}", response_model=ScenarioResponse)
async def delete_scenario(scenario_id: int):
    """刪除場景"""
    conn = await get_db_connection()
    try:
        row = await conn.fetchrow("DELETE FROM scenarios WHERE id = $1 RETURNING *", scenario_id)
        if not row:
            raise HTTPException(status_code=404, detail=f"場景 {scenario_id} 不存在")
        
        logger.info(f"場景已刪除: {scenario_id}")
        return ScenarioResponse(success=True, message="場景已刪除")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"刪除場景 {scenario_id} 失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()

