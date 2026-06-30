"""T13: 注册表（设计稿 §3.3）。"""
import pytest

from app.core import errors
from app import registry
from app.drivers.clickhouse import ClickHouseDriver
from app.drivers.redis import RedisDriver
from app.drivers.elasticsearch import ElasticsearchDriver
from app.drivers.kafka import KafkaDriver
from app.drivers.everest import EverestDriver


def test_seven_engines_registered():
    assert set(registry.REGISTRY.keys()) == {
        "mysql", "postgresql", "mongodb", "clickhouse", "redis", "elasticsearch", "kafka",
    }


@pytest.mark.parametrize("engine,cls", [
    ("clickhouse", ClickHouseDriver),
    ("redis", RedisDriver),
    ("elasticsearch", ElasticsearchDriver),
    ("kafka", KafkaDriver),
])
def test_k8s_drivers(engine, cls):
    assert isinstance(registry.get_driver(engine), cls)


@pytest.mark.parametrize("engine", ["mysql", "postgresql", "mongodb"])
def test_everest_drivers_carry_engine(engine):
    d = registry.get_driver(engine)
    assert isinstance(d, EverestDriver)
    assert d.engine_type == engine


def test_unknown_engine_raises():
    with pytest.raises((errors.NotFoundError, ValueError)):
        registry.get_driver("oracle")
