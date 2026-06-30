"""数据库管理 API（设计稿 §四）。

engine_type 放置规则：建库走 body（资源尚不存在，与参数一起校验），
其余操作走 URL path（资源已存在，作为资源坐标）。
"""
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError

from app.core import status as st
from app.models.specs import EngineType, spec_for
from app.registry import get_driver

router = APIRouter()

# 引擎及版本（GET /database-engines 用）——本轮静态列出
_ENGINES = [
    {"engine_type": "mysql", "versions": ["8.0.42-33.1"]},
    {"engine_type": "postgresql", "versions": ["16"]},
    {"engine_type": "mongodb", "versions": ["7.0"]},
    {"engine_type": "clickhouse", "versions": ["24.3"]},
    {"engine_type": "redis", "versions": ["7"]},
    {"engine_type": "elasticsearch", "versions": ["8.13.0"]},
    {"engine_type": "kafka", "versions": ["4.1.0"]},
]


class CreateRequest(BaseModel):
    """建库请求的最小外壳：engine_type 必在 body，其余字段透传给对应 Spec 校验。"""
    name: str
    engine_type: EngineType

    model_config = {"extra": "allow"}


@router.get("/healthz")
def healthz():
    return {"status": "ok"}


@router.get("/database-engines")
def database_engines():
    return {"engines": _ENGINES}


@router.post("/databases", status_code=202)
def create_database(payload: dict):
    # engine_type 在 body；按它选对应 Spec 严格校验（格式错 → ValidationError → 400）
    engine_type = payload.get("engine_type")
    spec = spec_for(engine_type, payload)  # 可能抛 ValidationError / ValueError
    driver = get_driver(engine_type)
    result = driver.create(spec)
    return result


@router.get("/databases/{engine_type}/{name}")
def get_database(engine_type: str, name: str):
    return get_driver(engine_type).get(name)


@router.get("/databases/{engine_type}")
def list_databases(engine_type: str):
    return {"items": get_driver(engine_type).list()}


@router.delete("/databases/{engine_type}/{name}", status_code=202)
def delete_database(engine_type: str, name: str):
    get_driver(engine_type).delete(name)
    return {"name": name, "status": st.DELETING}


@router.get("/databases/{engine_type}/{name}/connection")
def get_connection(engine_type: str, name: str) -> Any:
    conn = get_driver(engine_type).connection(name)
    # 连接对象是 Pydantic 模型，序列化为 dict（含 type 判别字段）
    return conn.model_dump() if hasattr(conn, "model_dump") else conn
