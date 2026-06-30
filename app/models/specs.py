"""参数模型（设计稿 §五）。

每引擎一张专属表单：公共参数放 BaseSpec，特有参数（目前仅 ClickHouse 的 shards）
在子类显式声明。Swagger 据此自动列出「建某库需要哪些参数」，前台据此渲染表单。

校验规则：name 不提前查重（靠底层报 409）；cpu/memory/storage 用正则严格校验，
格式错立刻 400。
"""
import re
from enum import Enum
from typing import Type

from pydantic import BaseModel, Field, field_validator

# K8s 命名：小写字母开头，仅小写字母/数字/连字符，≤63
_NAME_RE = re.compile(r"^[a-z][a-z0-9-]*$")
# cpu：核数（整数/小数）或毫核（如 500m）
_CPU_RE = re.compile(r"^(\d+(\.\d+)?|\d+m)$")
# memory/storage：必须二进制单位 Gi/Mi（设计稿踩坑：不能用 G/M）
_QTY_RE = re.compile(r"^\d+(Gi|Mi)$")


class EngineType(str, Enum):
    mysql = "mysql"
    postgresql = "postgresql"
    mongodb = "mongodb"
    clickhouse = "clickhouse"
    redis = "redis"
    elasticsearch = "elasticsearch"
    kafka = "kafka"


class BaseSpec(BaseModel):
    name: str = Field(..., max_length=63)
    engine_type: EngineType
    cpu: str
    memory: str
    storage: str
    replicas: int = Field(default=1, ge=1)

    @field_validator("name")
    @classmethod
    def _check_name(cls, v: str) -> str:
        if not _NAME_RE.match(v):
            raise ValueError("name 必须小写字母开头，仅含小写字母/数字/连字符")
        return v

    @field_validator("cpu")
    @classmethod
    def _check_cpu(cls, v: str) -> str:
        if not _CPU_RE.match(v):
            raise ValueError("cpu 格式错，应如 '1' / '0.5' / '500m'")
        return v

    @field_validator("memory", "storage")
    @classmethod
    def _check_qty(cls, v: str) -> str:
        if not _QTY_RE.match(v):
            raise ValueError("内存/存储必须用二进制单位，如 '2Gi' / '512Mi'")
        return v


class ClickHouseSpec(BaseSpec):
    shards: int = Field(default=1, ge=1)


class RedisSpec(BaseSpec):
    pass


class ElasticsearchSpec(BaseSpec):
    pass


class KafkaSpec(BaseSpec):
    pass


class MySQLSpec(BaseSpec):
    pass


class PostgreSQLSpec(BaseSpec):
    pass


class MongoDBSpec(BaseSpec):
    pass


# engine_type → 对应 Spec 类
SPEC_BY_ENGINE: dict[str, Type[BaseSpec]] = {
    "mysql": MySQLSpec,
    "postgresql": PostgreSQLSpec,
    "mongodb": MongoDBSpec,
    "clickhouse": ClickHouseSpec,
    "redis": RedisSpec,
    "elasticsearch": ElasticsearchSpec,
    "kafka": KafkaSpec,
}


def spec_for(engine_type: str, payload: dict) -> BaseSpec:
    """按 engine_type 选对应 Spec 类做校验。未知类型抛 ValueError。"""
    cls = SPEC_BY_ENGINE.get(engine_type)
    if cls is None:
        raise ValueError(f"不支持的引擎类型: {engine_type}")
    return cls(**payload)
