"""T11: Kafka 驱动（双资源 Kafka + KafkaNodePool，KRaft）。"""
from unittest.mock import MagicMock, call

import pytest
from kubernetes.client import ApiException

from app.core import status
from app.models.connection import KafkaConn
from app.models.specs import KafkaSpec
from app.drivers import kafka as kafka_mod
from app.drivers.kafka import KafkaDriver


def _spec(**kw):
    base = dict(name="kafka-01", engine_type="kafka", cpu="1", memory="2Gi", storage="20Gi")
    base.update(kw)
    return KafkaSpec(**base)


def test_kafka_body_kraft():
    d = KafkaDriver()
    body = d._kafka_body(_spec())
    assert body["kind"] == "Kafka"
    assert body["spec"]["kafka"]["version"] == "4.1.0"
    assert body["spec"]["kafka"]["metadataVersion"] == "4.1-IV0"


def test_nodepool_name_per_instance():
    # 修 bug：NodePool 名按实例派生，不再写死 "controller"
    d = KafkaDriver()
    body = d._nodepool_body(_spec(name="kafka-01"))
    assert body["kind"] == "KafkaNodePool"
    assert body["metadata"]["name"] == "kafka-01-pool"
    assert body["metadata"]["labels"]["strimzi.io/cluster"] == "kafka-01"
    assert body["spec"]["roles"] == ["controller", "broker"]


def test_two_instances_dont_collide():
    d = KafkaDriver()
    n1 = d._nodepool_body(_spec(name="kafka-01"))["metadata"]["name"]
    n2 = d._nodepool_body(_spec(name="kafka-02"))["metadata"]["name"]
    assert n1 != n2


@pytest.fixture
def mock_api(monkeypatch):
    api = MagicMock()
    monkeypatch.setattr(kafka_mod, "get_custom_api", lambda: api)
    return api


def test_create_kafka_before_nodepool(mock_api):
    d = KafkaDriver()
    d.create(_spec())
    plurals = [c.args[3] for c in mock_api.create_namespaced_custom_object.call_args_list]
    assert plurals == ["kafkas", "kafkanodepools"]


def test_delete_nodepool_before_kafka(mock_api):
    d = KafkaDriver()
    d.delete("kafka-01")
    plurals = [c.args[3] for c in mock_api.delete_namespaced_custom_object.call_args_list]
    assert plurals == ["kafkanodepools", "kafkas"]


def test_delete_tolerates_missing_nodepool(mock_api):
    def side(*args, **kwargs):
        if args[3] == "kafkanodepools":
            raise ApiException(status=404)
    mock_api.delete_namespaced_custom_object.side_effect = side
    d = KafkaDriver()
    d.delete("kafka-01")  # 不应抛错
    # kafka 仍被删
    assert any(c.args[3] == "kafkas" for c in mock_api.delete_namespaced_custom_object.call_args_list)


def test_parse_status_conditions():
    d = KafkaDriver()
    assert d.parse_status({"conditions": [{"type": "Ready", "status": "True"}]}) == status.READY
    assert d.parse_status({"conditions": [{"type": "NotReady", "status": "True", "reason": "x"}]}) == status.ERROR
    assert d.parse_status({"conditions": []}) == status.CREATING


def test_parse_connection():
    d = KafkaDriver()
    c = d.parse_connection("kafka-01")
    assert isinstance(c, KafkaConn)
    assert c.bootstrap_servers == "kafka-01-kafka-bootstrap.kafka.svc:9092"
    assert c.security == "PLAINTEXT"
