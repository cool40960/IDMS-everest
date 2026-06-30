"""T7: K8sDriver 中间基类（设计稿 §3.2）。

用一个假子类验证基类的共性逻辑：CRUD 调对了 K8s API、错误归一、IDMS 标签。
"""
from unittest.mock import MagicMock

import pytest
from kubernetes.client import ApiException

from app.core import errors, status
from app.models.specs import BaseSpec


@pytest.fixture
def fake_driver(monkeypatch):
    """一个最小可用的 K8sDriver 子类 + mock 掉 CustomObjectsApi。"""
    from app.drivers import k8s_base

    api = MagicMock()
    monkeypatch.setattr(k8s_base, "get_custom_api", lambda: api)

    class FakeDriver(k8s_base.K8sDriver):
        GROUP = "example.com"
        VERSION = "v1"
        PLURAL = "widgets"
        NAMESPACE = "demo"
        ENGINE = "redis"  # 借用一个合法 engine_type

        def build_body(self, spec):
            return {"metadata": {"name": spec.name}, "spec": {}}

        def parse_status(self, raw):
            return status.READY if raw.get("status") == "ok" else status.CREATING

        def parse_connection(self, name):
            return {"type": "redis", "host": f"{name}.demo", "port": 6379}

    return FakeDriver(), api


def _spec(name="w1"):
    return BaseSpec(name=name, engine_type="redis", cpu="1", memory="2Gi", storage="20Gi")


def test_create_calls_api_and_stamps_labels(fake_driver):
    driver, api = fake_driver
    driver.create(_spec("w1"))
    args, kwargs = api.create_namespaced_custom_object.call_args
    body = args[4] if len(args) > 4 else kwargs["body"]
    labels = body["metadata"]["labels"]
    assert labels["idms.io/managed"] == "true"
    assert labels["idms.io/engine"] == "redis"


def test_create_409_maps_to_already_exists(fake_driver):
    driver, api = fake_driver
    api.create_namespaced_custom_object.side_effect = ApiException(status=409)
    with pytest.raises(errors.AlreadyExistsError):
        driver.create(_spec())


def test_create_other_error_maps_to_upstream(fake_driver):
    driver, api = fake_driver
    api.create_namespaced_custom_object.side_effect = ApiException(status=500)
    with pytest.raises(errors.UpstreamError):
        driver.create(_spec())


def test_get_parses_status(fake_driver):
    driver, api = fake_driver
    api.get_namespaced_custom_object.return_value = {"status": {"status": "ok"}}
    result = driver.get("w1")
    assert result["status"] == status.READY
    assert result["name"] == "w1"
    assert result["engine_type"] == "redis"


def test_get_404_maps_to_not_found(fake_driver):
    driver, api = fake_driver
    api.get_namespaced_custom_object.side_effect = ApiException(status=404)
    with pytest.raises(errors.NotFoundError):
        driver.get("missing")


def test_delete_calls_api(fake_driver):
    driver, api = fake_driver
    driver.delete("w1")
    api.delete_namespaced_custom_object.assert_called_once()


def test_delete_404_maps_to_not_found(fake_driver):
    driver, api = fake_driver
    api.delete_namespaced_custom_object.side_effect = ApiException(status=404)
    with pytest.raises(errors.NotFoundError):
        driver.delete("missing")


def test_list_filters_by_idms_label(fake_driver):
    driver, api = fake_driver
    api.list_namespaced_custom_object.return_value = {
        "items": [
            {"metadata": {"name": "a", "labels": {"idms.io/managed": "true"}}, "status": {"status": "ok"}},
            {"metadata": {"name": "b", "labels": {}}, "status": {}},  # 手工建的，过滤掉
        ]
    }
    items = driver.list()
    names = [i["name"] for i in items]
    assert names == ["a"]
