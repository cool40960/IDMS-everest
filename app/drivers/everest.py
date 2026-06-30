"""Everest 驱动（改自原 everest_api.py，设计稿 §九）。

服务 mysql / postgresql / mongodb，走 OpenEverest REST API（:8080）。
原代码缺两个必需项，这里补上：
  ① JWT 登录：POST /v1/session 拿 token，后续请求带 Authorization: Bearer。
     token 约 24h 过期，401 时自动重新登录重试一次。
  ② engine.type 映射（实测，不映射建不出库）：mysql→pxc / mongodb→psmdb / postgresql→postgresql。
账密从环境变量 EVEREST_USER / EVEREST_PASSWORD 读，不硬编码。
"""
import os

import requests

from app.core import errors, status
from app.drivers.base import DatabaseDriver
from app.models.connection import MySQLConn, PostgreSQLConn, MongoDBConn

EVEREST_HOST = os.environ.get("EVEREST_HOST", "http://10.10.214.193:8080")
_BASE = f"{EVEREST_HOST}/v1/namespaces/everest"
_SESSION_URL = f"{EVEREST_HOST}/v1/session"

# 用户层 engine_type → Everest spec.engine.type（实测）
_TYPE_MAP = {"mysql": "pxc", "mongodb": "psmdb", "postgresql": "postgresql"}
_CONN_CLS = {"mysql": MySQLConn, "postgresql": PostgreSQLConn, "mongodb": MongoDBConn}


class EverestDriver(DatabaseDriver):
    def __init__(self, engine_type: str):
        self.engine_type = engine_type
        self._token = None

    def _everest_type(self) -> str:
        return _TYPE_MAP[self.engine_type]

    # ---- JWT ----
    def _login(self) -> str:
        user = os.environ.get("EVEREST_USER")
        password = os.environ.get("EVEREST_PASSWORD")
        if not user or not password:
            raise errors.UpstreamError("缺少 EVEREST_USER / EVEREST_PASSWORD 环境变量")
        resp = requests.post(_SESSION_URL, json={"username": user, "password": password})
        if resp.status_code != 200:
            raise errors.UpstreamError(f"Everest 登录失败: {resp.status_code}")
        self._token = resp.json()["token"]
        return self._token

    def _auth_headers(self) -> dict:
        if not self._token:
            self._login()
        return {"Authorization": f"Bearer {self._token}"}

    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        """带鉴权发请求；401 自动重登重试一次。"""
        resp = requests.request(method, url, headers=self._auth_headers(), **kwargs)
        if resp.status_code == 401:
            self._login()
            resp = requests.request(method, url, headers=self._auth_headers(), **kwargs)
        return resp

    @staticmethod
    def _check(resp: requests.Response, name: str) -> requests.Response:
        if resp.status_code == 404:
            raise errors.NotFoundError(f"实例 {name} 不存在")
        if resp.status_code == 409:
            raise errors.AlreadyExistsError(f"实例 {name} 已存在")
        if resp.status_code >= 500 or resp.status_code == 400:
            raise errors.UpstreamError(f"Everest API 故障: {resp.status_code}")
        return resp

    # ---- CRUD ----
    def create(self, spec) -> dict:
        body = {
            "apiVersion": "everest.percona.com/v1alpha1",
            "kind": "DatabaseCluster",
            "metadata": {
                "name": spec.name,
                "labels": {"idms.io/managed": "true", "idms.io/engine": self.engine_type},
            },
            "spec": {
                "engine": {
                    "type": self._everest_type(),  # 映射！
                    "replicas": spec.replicas,
                    "userSecretsName": f"{spec.name}-secret",
                    "resources": {"cpu": spec.cpu, "memory": spec.memory},
                    "storage": {"size": spec.storage},
                },
                "proxy": {"type": "haproxy", "replicas": 1},
                "allowUnsafeConfiguration": True,
            },
        }
        resp = self._request("POST", f"{_BASE}/database-clusters", json=body)
        self._check(resp, spec.name)
        return {"name": spec.name, "engine_type": self.engine_type, "status": status.CREATING}

    def get(self, name: str) -> dict:
        resp = self._request("GET", f"{_BASE}/database-clusters/{name}")
        self._check(resp, name)
        data = resp.json()
        raw = data.get("status", {})
        return {
            "name": name,
            "engine_type": self.engine_type,
            "status": self.parse_status(raw),
            "message": raw.get("details", "") if isinstance(raw, dict) else "",
            "raw": raw,
        }

    def delete(self, name: str) -> None:
        resp = self._request("DELETE", f"{_BASE}/database-clusters/{name}")
        self._check(resp, name)

    def list(self) -> list[dict]:
        resp = self._request("GET", f"{_BASE}/database-clusters")
        self._check(resp, "")
        out = []
        for item in resp.json().get("items", []):
            labels = item.get("metadata", {}).get("labels", {}) or {}
            if labels.get("idms.io/engine") != self.engine_type:
                continue
            out.append({
                "name": item["metadata"]["name"],
                "engine_type": self.engine_type,
                "status": self.parse_status(item.get("status", {})),
            })
        return out

    def parse_status(self, raw) -> str:
        s = raw.get("status") if isinstance(raw, dict) else None
        mapping = {
            "ready": status.READY,
            "error": status.ERROR,
            "initializing": status.INITIALIZING,
            "creating": status.CREATING,
            "deleting": status.DELETING,
        }
        return mapping.get(s, status.CREATING)

    def connection(self, name: str):
        # host/port 取实例 status；账密调 credentials 接口（仅 ready 可取）
        resp = self._request("GET", f"{_BASE}/database-clusters/{name}")
        self._check(resp, name)
        st = resp.json().get("status", {})
        cred = self._request("GET", f"{_BASE}/database-clusters/{name}/credentials")
        self._check(cred, name)
        c = cred.json()
        cls = _CONN_CLS[self.engine_type]
        return cls(
            host=st.get("hostname", ""),
            port=st.get("port", 0),
            username=c.get("username", ""),
            password=c.get("password", ""),
        )
