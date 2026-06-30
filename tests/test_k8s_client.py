"""T3: 公共 K8s 客户端（设计稿 §十一 core）。

改造自原 k8s_client.py：原来只暴露 CustomObjectsApi，这里补 CoreV1Api
（Redis 查 Pod / 读 Secret）和 AppsV1Api（Redis 查 StatefulSet/Deployment），
并让 config 只加载一次。
"""
import importlib

import pytest


@pytest.fixture
def k8s_client(monkeypatch):
    """每个测试拿一份重置过加载状态的模块，并 mock 掉 kubernetes。"""
    from app.core import k8s_client as mod

    importlib.reload(mod)

    calls = {"incluster": 0, "kube": 0}

    def fake_incluster():
        calls["incluster"] += 1

    def fake_kube(config_file=None):
        calls["kube"] += 1

    monkeypatch.setattr(mod.config, "load_incluster_config", fake_incluster)
    monkeypatch.setattr(mod.config, "load_kube_config", fake_kube)
    return mod, calls


def test_three_getters_return_right_api(k8s_client):
    mod, _ = k8s_client
    from kubernetes import client

    assert isinstance(mod.get_custom_api(), client.CustomObjectsApi)
    assert isinstance(mod.get_core_api(), client.CoreV1Api)
    assert isinstance(mod.get_apps_api(), client.AppsV1Api)


def test_config_loaded_once(k8s_client):
    mod, calls = k8s_client
    mod.get_custom_api()
    mod.get_core_api()
    mod.get_apps_api()
    mod.get_custom_api()
    # 即使调用四次，config 只加载一次
    assert calls["incluster"] == 1
    assert calls["kube"] == 0


def test_fallback_to_kube_config(k8s_client, monkeypatch):
    mod, calls = k8s_client
    from kubernetes import config as kconfig

    def boom():
        raise kconfig.ConfigException("not in cluster")

    monkeypatch.setattr(mod.config, "load_incluster_config", boom)
    mod.get_core_api()
    # in-cluster 失败 → 回退 kube_config
    assert calls["kube"] == 1
