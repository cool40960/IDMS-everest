"""翻译层驱动抽象基类（设计稿 §3.1）。

定义所有驱动必须实现的「动作契约」——类比 JDBC：上层只认统一接口，
不认具体库。两条路径（K8s / Everest）只是两种实现，对上层透明。

统一状态词见 app.core.status；连接对象见 app.models.connection。
"""
from abc import ABC, abstractmethod
from typing import Any


class DatabaseDriver(ABC):
    @abstractmethod
    def create(self, spec) -> dict:
        """按统一参数建库。返回实例标识（含 name/engine_type/status）。"""

    @abstractmethod
    def get(self, name: str) -> dict:
        """查实例。返回统一状态：creating/initializing/ready/error/deleting。"""

    @abstractmethod
    def delete(self, name: str) -> None:
        """删实例。"""

    @abstractmethod
    def list(self) -> list[dict]:
        """列出本引擎所有 IDMS 管理的实例。"""

    @abstractmethod
    def connection(self, name: str) -> Any:
        """取连接信息。返回带 type 的连接对象（见 app.models.connection）。"""
