"""T5: 连接对象模型（设计稿 §七，带 type 的判别联合）。"""
import pytest
from pydantic import TypeAdapter, ValidationError

from app.models import connection as conn


def test_mysql_conn_fields():
    c = conn.MySQLConn(host="h", port=3306, username="root", password="p")
    assert c.type == "mysql"
    assert c.model_dump()["type"] == "mysql"


def test_clickhouse_has_http_port():
    c = conn.ClickHouseConn(host="h", port=9000, username="idms", password="p")
    assert c.http_port == 8123
    assert c.type == "clickhouse"


def test_elasticsearch_https_defaults():
    c = conn.ElasticsearchConn(host="h", port=9200, password="p")
    assert c.scheme == "https"
    assert c.username == "elastic"
    assert c.ca_cert is None


def test_kafka_no_credentials():
    c = conn.KafkaConn(host="h", port=9092, bootstrap_servers="h:9092")
    assert c.type == "kafka"
    assert c.security == "PLAINTEXT"
    # Kafka 没有 username/password 字段
    assert "username" not in c.model_dump()
    assert "password" not in c.model_dump()


def test_redis_optional_sentinel():
    c = conn.RedisConn(host="h", port=6379, password="p")
    assert c.sentinel is None
    c2 = conn.RedisConn(
        host="h", port=6379, password="p",
        sentinel={"host": "s", "port": 26379, "master_name": "mymaster"},
    )
    assert c2.sentinel.port == 26379


def test_discriminated_union_parses_by_type():
    adapter = TypeAdapter(conn.Connection)
    obj = adapter.validate_python(
        {"type": "kafka", "host": "h", "port": 9092, "bootstrap_servers": "h:9092"}
    )
    assert isinstance(obj, conn.KafkaConn)

    obj2 = adapter.validate_python(
        {"type": "redis", "host": "h", "port": 6379, "password": "x"}
    )
    assert isinstance(obj2, conn.RedisConn)


def test_union_rejects_unknown_type():
    adapter = TypeAdapter(conn.Connection)
    with pytest.raises(ValidationError):
        adapter.validate_python({"type": "oracle", "host": "h", "port": 1})
