"""Kafka 驱动（改自原 k8s_kafka.py，设计稿 §六/§十）。

CRD: Kafka + KafkaNodePool（Strimzi，KRaft 模式，双资源缺一不可）。
改进：原代码 NodePool 名写死 "controller"，多实例会撞名——这里按实例名派生。
顺序：建先 Kafka 后 NodePool，删反序（先 NodePool 后 Kafka，404 容忍）。
就绪判定：status.conditions 有 Ready/True；NotReady/True → error。
连接：bootstrap servers，内部 plain listener:9092，无账密（PLAINTEXT）。
"""
from kubernetes.client import ApiException

from app.core import errors, status
from app.core.k8s_client import get_custom_api
from app.drivers.k8s_base import K8sDriver
from app.models.connection import KafkaConn

KAFKA_VERSION = "4.1.0"
KAFKA_META_VERSION = "4.1-IV0"


class KafkaDriver(K8sDriver):
    GROUP = "kafka.strimzi.io"
    VERSION = "v1"
    PLURAL = "kafkas"               # 主资源（基类 get/list 用这个）
    NODEPOOL_PLURAL = "kafkanodepools"
    NAMESPACE = "kafka"
    ENGINE = "kafka"

    def _nodepool_name(self, name: str) -> str:
        return f"{name}-pool"

    def _kafka_body(self, spec) -> dict:
        return {
            "apiVersion": f"{self.GROUP}/{self.VERSION}",
            "kind": "Kafka",
            "metadata": {
                "name": spec.name,
                "namespace": self.NAMESPACE,
                # KRaft + NodePool 模式开关
                "annotations": {
                    "strimzi.io/kraft": "enabled",
                    "strimzi.io/node-pools": "enabled",
                },
            },
            "spec": {
                "kafka": {
                    "version": KAFKA_VERSION,
                    "metadataVersion": KAFKA_META_VERSION,
                    "listeners": [
                        {"name": "plain", "port": 9092, "type": "internal", "tls": False},
                        {"name": "tls", "port": 9093, "type": "internal", "tls": True},
                    ],
                    "config": {
                        "offsets.topic.replication.factor": "1",
                        "transaction.state.log.replication.factor": "1",
                        "transaction.state.log.min.isr": "1",
                        "default.replication.factor": "1",
                        "min.insync.replicas": "1",
                    },
                },
                "entityOperator": {"topicOperator": {}, "userOperator": {}},
            },
        }

    def _nodepool_body(self, spec) -> dict:
        return {
            "apiVersion": f"{self.GROUP}/{self.VERSION}",
            "kind": "KafkaNodePool",
            "metadata": {
                "name": self._nodepool_name(spec.name),  # 按实例派生，修撞名
                "namespace": self.NAMESPACE,
                "labels": {"strimzi.io/cluster": spec.name},
            },
            "spec": {
                "replicas": spec.replicas,
                "roles": ["controller", "broker"],
                "storage": {
                    "type": "jbod",
                    "volumes": [{
                        "id": 0,
                        "type": "persistent-claim",
                        "size": spec.storage,
                        "deleteClaim": False,
                    }],
                },
                "resources": {
                    "requests": {"cpu": spec.cpu, "memory": spec.memory},
                    "limits": {"cpu": spec.cpu, "memory": spec.memory},
                },
            },
        }

    # override：双资源，建先 Kafka 后 NodePool
    def create(self, spec) -> dict:
        api = get_custom_api()
        kafka = self._stamp_labels(self._kafka_body(spec))
        pool = self._stamp_labels(self._nodepool_body(spec))
        try:
            api.create_namespaced_custom_object(self.GROUP, self.VERSION, self.NAMESPACE, self.PLURAL, kafka)
            api.create_namespaced_custom_object(self.GROUP, self.VERSION, self.NAMESPACE, self.NODEPOOL_PLURAL, pool)
        except ApiException as e:
            raise self._map_error(e, spec.name)
        return {"name": spec.name, "engine_type": self.ENGINE, "status": status.CREATING}

    # override：删反序，先 NodePool（404 容忍）后 Kafka
    def delete(self, name: str) -> None:
        api = get_custom_api()
        try:
            api.delete_namespaced_custom_object(
                self.GROUP, self.VERSION, self.NAMESPACE, self.NODEPOOL_PLURAL, self._nodepool_name(name)
            )
        except ApiException as e:
            if e.status != 404:
                raise self._map_error(e, name)
        try:
            api.delete_namespaced_custom_object(
                self.GROUP, self.VERSION, self.NAMESPACE, self.PLURAL, name
            )
        except ApiException as e:
            raise self._map_error(e, name)

    def parse_status(self, raw: dict) -> str:
        conditions = raw.get("conditions", []) or []
        for c in conditions:
            if c.get("type") == "Ready" and c.get("status") == "True":
                return status.READY
            if c.get("type") == "NotReady" and c.get("status") == "True":
                return status.ERROR
        return status.CREATING

    def parse_connection(self, name: str) -> KafkaConn:
        return KafkaConn(
            host=f"{name}-kafka-bootstrap.{self.NAMESPACE}.svc",
            port=9092,
            bootstrap_servers=f"{name}-kafka-bootstrap.{self.NAMESPACE}.svc:9092",
            security="PLAINTEXT",
        )
