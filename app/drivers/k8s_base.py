"""K8sDriver 中间基类（设计稿 §3.2）。

四个 K8s 库「怎么调 K8s API、怎么从 CRD 读 status、怎么归一错误」几乎一样，
只有「CRD body 长啥样」「status 怎么解析」「去哪取连接」不同。把共性提到这里，
子类只实现差异：
    GROUP / VERSION / PLURAL / NAMESPACE / ENGINE  —— CRD 坐标
    build_body(spec)        —— 参数 → CRD body（字段映射核心）
    parse_status(raw)       —— 原始 status → 统一状态词
    parse_connection(name)  —— 去哪个 Secret/Service 取连接信息

错误统一归一到 app.core.errors（设计稿 §八）。
"""
from typing import Any

from kubernetes.client import ApiException

from app.core import errors, status
from app.core.k8s_client import get_custom_api
from app.drivers.base import DatabaseDriver

MANAGED_LABEL = "idms.io/managed"
ENGINE_LABEL = "idms.io/engine"


class K8sDriver(DatabaseDriver):
    # 子类必填的 CRD 坐标
    GROUP: str = ""
    VERSION: str = ""
    PLURAL: str = ""
    NAMESPACE: str = ""
    ENGINE: str = ""

    # ---- 子类实现的差异钩子 ----
    def build_body(self, spec) -> dict:
        raise NotImplementedError

    def parse_status(self, raw: dict) -> str:
        raise NotImplementedError

    def parse_connection(self, name: str) -> Any:
        raise NotImplementedError

    # ---- 共性：CRUD ----
    def _stamp_labels(self, body: dict) -> dict:
        meta = body.setdefault("metadata", {})
        labels = meta.setdefault("labels", {})
        labels[MANAGED_LABEL] = "true"
        labels[ENGINE_LABEL] = self.ENGINE
        return body

    def create(self, spec) -> dict:
        body = self._stamp_labels(self.build_body(spec))
        api = get_custom_api()
        try:
            api.create_namespaced_custom_object(
                self.GROUP, self.VERSION, self.NAMESPACE, self.PLURAL, body
            )
        except ApiException as e:
            raise self._map_error(e, spec.name)
        return {"name": spec.name, "engine_type": self.ENGINE, "status": status.CREATING}

    def get(self, name: str) -> dict:
        api = get_custom_api()
        try:
            obj = api.get_namespaced_custom_object(
                self.GROUP, self.VERSION, self.NAMESPACE, self.PLURAL, name
            )
        except ApiException as e:
            raise self._map_error(e, name)
        raw = obj.get("status", {})
        return {
            "name": name,
            "engine_type": self.ENGINE,
            "status": self.parse_status(raw),
            "message": self._message(raw),
            "raw": raw,
        }

    def delete(self, name: str) -> None:
        api = get_custom_api()
        try:
            api.delete_namespaced_custom_object(
                self.GROUP, self.VERSION, self.NAMESPACE, self.PLURAL, name
            )
        except ApiException as e:
            raise self._map_error(e, name)

    def list(self) -> list[dict]:
        api = get_custom_api()
        try:
            resp = api.list_namespaced_custom_object(
                self.GROUP, self.VERSION, self.NAMESPACE, self.PLURAL
            )
        except ApiException as e:
            raise self._map_error(e, "")
        items = []
        for obj in resp.get("items", []):
            labels = obj.get("metadata", {}).get("labels", {}) or {}
            if labels.get(MANAGED_LABEL) != "true":
                continue  # 只列 IDMS 管理的，过滤手工建的
            items.append({
                "name": obj["metadata"]["name"],
                "engine_type": self.ENGINE,
                "status": self.parse_status(obj.get("status", {})),
            })
        return items

    def connection(self, name: str) -> Any:
        return self.parse_connection(name)

    # ---- 共性：错误归一 ----
    @staticmethod
    def _map_error(e: ApiException, name: str) -> errors.IDMSError:
        if e.status == 404:
            return errors.NotFoundError(f"实例 {name} 不存在")
        if e.status == 409:
            return errors.AlreadyExistsError(f"实例 {name} 已存在")
        return errors.UpstreamError(f"K8s API 故障: {e.status} {e.reason}")

    @staticmethod
    def _message(raw: dict) -> str:
        """默认从 status 里捞个可读信息，子类可不管。"""
        return raw.get("message", "") if isinstance(raw, dict) else ""
