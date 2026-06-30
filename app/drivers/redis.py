"""Redis 驱动（改自原 k8s_redis.py，设计稿 §6.1）。

CRD: RedisFailover（Spotahome operator）。隐藏参数：sentinel.replicas=3。

⚠️ 重点：RedisFailover CRD 不暴露 status，无法从 CRD 读就绪。override get()，
改查 operator 建的两个工作负载的 readyReplicas：
    StatefulSet rfr-<name>  —— redis 主从
    Deployment  rfs-<name>  —— sentinel
两者 readyReplicas 都达到各自 spec.replicas 才算 ready。查 readyReplicas 比逐个数
Pod 更稳（扩容/滚动更新期间不会误判）。

运维约束：实测 redis-operator 镜像为 :latest 未锁版本，rfr-/rfs- 命名契约随
operator 版本可能变化，升级前需回归本驱动。
"""
from kubernetes.client import ApiException

from app.core import errors, status
from app.core.k8s_client import get_apps_api, get_custom_api
from app.drivers.k8s_base import K8sDriver
from app.models.connection import RedisConn

# 连接密码读 operator 生成的 Secret —— Secret 名留待冒烟阶段连集群确认（设计稿 §七）
_CONN_PASSWORD_PLACEHOLDER = "TODO-confirm-secret"


class RedisDriver(K8sDriver):
    GROUP = "databases.spotahome.com"
    VERSION = "v1"
    PLURAL = "redisfailovers"
    NAMESPACE = "default"
    ENGINE = "redis"

    def build_body(self, spec) -> dict:
        return {
            "apiVersion": f"{self.GROUP}/{self.VERSION}",
            "kind": "RedisFailover",
            "metadata": {"name": spec.name, "namespace": self.NAMESPACE},
            "spec": {
                "redis": {
                    "replicas": spec.replicas,
                    "resources": {
                        "requests": {"cpu": spec.cpu, "memory": spec.memory},
                        "limits": {"cpu": spec.cpu, "memory": spec.memory},
                    },
                    "storage": {
                        "persistentVolumeClaim": {
                            "metadata": {"name": f"{spec.name}-data"},
                            "spec": {
                                "accessModes": ["ReadWriteOnce"],
                                "resources": {"requests": {"storage": spec.storage}},
                            },
                        }
                    },
                },
                "sentinel": {"replicas": 3},  # 隐藏参数写死
            },
        }

    # override：不读 CRD status，查工作负载就绪副本
    def get(self, name: str) -> dict:
        # 先确认 CRD 还在（删除后应 404 → NotFound）
        try:
            get_custom_api().get_namespaced_custom_object(
                self.GROUP, self.VERSION, self.NAMESPACE, self.PLURAL, name
            )
        except ApiException as e:
            if e.status == 404:
                raise errors.NotFoundError(f"实例 {name} 不存在")
            # CRD 读取本身故障不致命，继续靠工作负载判断
        st = self._workload_status(name)
        return {"name": name, "engine_type": self.ENGINE, "status": st, "message": "", "raw": {}}

    def _workload_status(self, name: str) -> str:
        apps = get_apps_api()
        rfr_ok = self._ready(lambda: apps.read_namespaced_stateful_set(f"rfr-{name}", self.NAMESPACE))
        if rfr_ok is None:
            return status.CREATING  # redis 工作负载还没建出来
        rfs_ok = self._ready(lambda: apps.read_namespaced_deployment(f"rfs-{name}", self.NAMESPACE))
        if rfs_ok is None:
            return status.CREATING  # sentinel 还没建出来
        return status.READY if (rfr_ok and rfs_ok) else status.INITIALIZING

    @staticmethod
    def _ready(reader):
        """返回 True/False（达标与否），或 None（工作负载不存在）。"""
        try:
            w = reader()
        except ApiException as e:
            if e.status == 404:
                return None
            raise errors.UpstreamError(f"查 Redis 工作负载故障: {e.status}")
        desired = w.spec.replicas or 0
        ready = w.status.ready_replicas or 0
        return ready >= desired and desired > 0

    # CRD 无 status，这个不会被基类调用，留个明确实现以防误用
    def parse_status(self, raw: dict) -> str:
        return status.CREATING

    def parse_connection(self, name: str) -> RedisConn:
        return RedisConn(
            host=f"rfs-{name}.{self.NAMESPACE}.svc",
            port=6379,
            password=_CONN_PASSWORD_PLACEHOLDER,
        )
