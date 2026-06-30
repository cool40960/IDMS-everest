"""ClickHouse 驱动（改自原 k8s_clickhouse.py）。

CRD: ClickHouseInstallation（Altinity operator）。
隐藏参数：账号 idms + networks/ip=::/0（见 idms-backend-translation-layer.md 第八节）。
就绪判定：status.status == "Completed"（实测 hostsCompleted/hosts 不可靠）。
"""
from app.core import status
from app.drivers.k8s_base import K8sDriver
from app.models.connection import ClickHouseConn

DEFAULT_USER = "idms"
DEFAULT_PASSWORD = "idms123456"  # 隐藏参数；连接信息用同一个
IMAGE = "clickhouse/clickhouse-server:24.3"


class ClickHouseDriver(K8sDriver):
    GROUP = "clickhouse.altinity.com"
    VERSION = "v1"
    PLURAL = "clickhouseinstallations"
    NAMESPACE = "clickhouse"
    ENGINE = "clickhouse"

    def build_body(self, spec) -> dict:
        return {
            "apiVersion": f"{self.GROUP}/{self.VERSION}",
            "kind": "ClickHouseInstallation",
            "metadata": {"name": spec.name, "namespace": self.NAMESPACE},
            "spec": {
                "configuration": {
                    "clusters": [{
                        "name": spec.name,
                        "layout": {
                            "shardsCount": spec.shards,
                            "replicasCount": spec.replicas,
                        },
                    }],
                    "users": {
                        f"{DEFAULT_USER}/password": DEFAULT_PASSWORD,
                        f"{DEFAULT_USER}/networks/ip": "::/0",
                        f"{DEFAULT_USER}/profile": "default",
                        f"{DEFAULT_USER}/quota": "default",
                    },
                },
                "defaults": {
                    "templates": {
                        "podTemplate": "pod-template",
                        "dataVolumeClaimTemplate": "data-volume",
                    }
                },
                "templates": {
                    "podTemplates": [{
                        "name": "pod-template",
                        "spec": {
                            "containers": [{
                                "name": "clickhouse",
                                "image": IMAGE,
                                "resources": {
                                    "requests": {"cpu": spec.cpu, "memory": spec.memory},
                                    "limits": {"cpu": spec.cpu, "memory": spec.memory},
                                },
                            }]
                        },
                    }],
                    "volumeClaimTemplates": [{
                        "name": "data-volume",
                        "spec": {
                            "accessModes": ["ReadWriteOnce"],
                            "resources": {"requests": {"storage": spec.storage}},
                        },
                    }],
                },
            },
        }

    def parse_status(self, raw: dict) -> str:
        s = raw.get("status")
        if s == "Completed":
            return status.READY
        if s:
            return status.INITIALIZING
        return status.CREATING

    def parse_connection(self, name: str) -> ClickHouseConn:
        return ClickHouseConn(
            host=f"clickhouse-{name}.{self.NAMESPACE}.svc",
            port=9000,
            http_port=8123,
            username=DEFAULT_USER,
            password=DEFAULT_PASSWORD,
        )
