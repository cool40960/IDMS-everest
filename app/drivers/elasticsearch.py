"""Elasticsearch 驱动（改自原 k8s_elasticsearch.py）。

CRD: Elasticsearch（ECK operator）。
改进：原代码 _heap 写死 256m，这里改为按 memory 推导（约容器内存一半）。
就绪判定：status.phase == "Ready"（health green/yellow/red 作健康度细分）。
连接：ECK 默认开 TLS，走 HTTPS，密码读 Secret {name}-es-elastic-user。
"""
import re

from app.core import status
from app.drivers.k8s_base import K8sDriver
from app.models.connection import ElasticsearchConn

_QTY_RE = re.compile(r"^(\d+)(Gi|Mi)$")
# 连接密码读 Secret {name}-es-elastic-user —— 留待冒烟阶段连集群确认（设计稿 §七）
_CONN_PASSWORD_PLACEHOLDER = "TODO-confirm-secret"


def derive_heap(memory: str) -> str:
    """从容器 memory 推导 ES JVM heap，取约一半。返回 ES_JAVA_OPTS 串。"""
    m = _QTY_RE.match(memory)
    if not m:
        return "-Xms512m -Xmx512m"
    val, unit = int(m.group(1)), m.group(2)
    mib = val * 1024 if unit == "Gi" else val
    half = mib // 2
    if half >= 1024 and half % 1024 == 0:
        size = f"{half // 1024}g"
    else:
        size = f"{half}m"
    return f"-Xms{size} -Xmx{size}"


class ElasticsearchDriver(K8sDriver):
    GROUP = "elasticsearch.k8s.elastic.co"
    VERSION = "v1"
    PLURAL = "elasticsearches"
    NAMESPACE = "elastic-system"
    ENGINE = "elasticsearch"

    def build_body(self, spec) -> dict:
        return {
            "apiVersion": f"{self.GROUP}/{self.VERSION}",
            "kind": "Elasticsearch",
            "metadata": {"name": spec.name, "namespace": self.NAMESPACE},
            "spec": {
                "version": "8.13.0",
                "nodeSets": [{
                    "name": "default",
                    "count": spec.replicas,
                    "config": {"node.store.allow_mmap": False},
                    "podTemplate": {
                        "spec": {
                            "containers": [{
                                "name": "elasticsearch",
                                "env": [{"name": "ES_JAVA_OPTS", "value": derive_heap(spec.memory)}],
                                "resources": {
                                    "requests": {"cpu": spec.cpu, "memory": spec.memory},
                                    "limits": {"cpu": spec.cpu, "memory": spec.memory},
                                },
                            }]
                        }
                    },
                    "volumeClaimTemplates": [{
                        "metadata": {"name": "elasticsearch-data"},
                        "spec": {
                            "accessModes": ["ReadWriteOnce"],
                            "resources": {"requests": {"storage": spec.storage}},
                        },
                    }],
                }],
            },
        }

    def parse_status(self, raw: dict) -> str:
        phase = raw.get("phase")
        if phase == "Ready":
            return status.READY
        if phase:
            return status.INITIALIZING
        return status.CREATING

    def parse_connection(self, name: str) -> ElasticsearchConn:
        return ElasticsearchConn(
            host=f"{name}-es-http.{self.NAMESPACE}.svc",
            port=9200,
            scheme="https",
            username="elastic",
            password=_CONN_PASSWORD_PLACEHOLDER,
        )
