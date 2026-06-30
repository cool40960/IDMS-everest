"""注册表（设计稿 §3.3）。

一张 engine_type → driver 查找表，分发逻辑收敛到这一处（取代 if-else）。
API 层拿到 engine_type，get_driver() 取出驱动调统一方法。加新库只动驱动层 +
这里登记一行，API 层永不需要改（开闭原则）。
"""
from app.core import errors
from app.drivers.base import DatabaseDriver
from app.drivers.clickhouse import ClickHouseDriver
from app.drivers.elasticsearch import ElasticsearchDriver
from app.drivers.everest import EverestDriver
from app.drivers.kafka import KafkaDriver
from app.drivers.redis import RedisDriver

REGISTRY: dict[str, DatabaseDriver] = {
    "mysql": EverestDriver("mysql"),
    "postgresql": EverestDriver("postgresql"),
    "mongodb": EverestDriver("mongodb"),
    "clickhouse": ClickHouseDriver(),
    "redis": RedisDriver(),
    "elasticsearch": ElasticsearchDriver(),
    "kafka": KafkaDriver(),
}


def get_driver(engine_type: str) -> DatabaseDriver:
    driver = REGISTRY.get(engine_type)
    if driver is None:
        raise errors.NotFoundError(f"不支持的引擎类型: {engine_type}")
    return driver
