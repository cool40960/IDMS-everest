"""公共 K8s 客户端（设计稿 §十一 core）。

改造自原 k8s_client.py。要点：
- in-cluster 优先（IDMS 部署为集群内 Pod），回退本地 kubeconfig（开发/测试）
- config 只加载一次（_loaded 标志），避免每次调用重复加载
- 暴露三个 API：
    CustomObjectsApi —— 读写各库 CRD（CK/Redis/ES/Kafka）
    CoreV1Api        —— Redis 读 Secret、查 Pod；各库取连接读 Secret
    AppsV1Api        —— Redis 查 StatefulSet(rfr-)/Deployment(rfs-) 就绪副本
"""
from kubernetes import client, config
import os

_loaded = False


def _ensure_config():
    global _loaded
    if _loaded:
        return
    try:
        config.load_incluster_config()
    except config.ConfigException:
        # 本地/冒烟：优先标准 KUBECONFIG 环境变量，回退默认 admin.conf
        kubeconfig = os.environ.get("KUBECONFIG")
        if kubeconfig:
            config.load_kube_config(config_file=kubeconfig)
        else:
            config.load_kube_config(config_file="/etc/kubernetes/admin.conf")
    _loaded = True


def get_custom_api():
    _ensure_config()
    return client.CustomObjectsApi()


def get_core_api():
    _ensure_config()
    return client.CoreV1Api()


def get_apps_api():
    _ensure_config()
    return client.AppsV1Api()
