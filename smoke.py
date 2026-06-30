#!/usr/bin/env python
"""端到端冒烟脚本（手动连真集群，不进单测/CI）。

对每个引擎跑「建小实例 → 轮询到 ready → 取连接 → 删除」一遍。
需要：① 集群可达（10.10.214.193）；② 路径一引擎需 EVEREST_USER/PASSWORD。

用法：
    # 全部引擎
    .venv/bin/python smoke.py
    # 只跑指定引擎
    .venv/bin/python smoke.py clickhouse mysql
    # 只跑路径二（不需要 Everest 账密）
    .venv/bin/python smoke.py clickhouse redis elasticsearch kafka

⚠️ 设计稿留的两处 TODO 在这里连集群核对并回填：
   - Redis 连接密码 Secret 名（app/drivers/redis.py: _CONN_PASSWORD_PLACEHOLDER）
   - Elasticsearch 连接密码 Secret 名（app/drivers/elasticsearch.py: 同名占位）
"""
import sys
import time

from app.core import status
from app.models.specs import spec_for
from app.registry import get_driver

ALL_ENGINES = ["clickhouse", "redis", "elasticsearch", "kafka", "mysql", "postgresql", "mongodb"]

# 每引擎一份最小建库参数
SMOKE_SPECS = {
    "clickhouse":    {"cpu": "500m", "memory": "1Gi", "storage": "10Gi", "shards": 1},
    "redis":         {"cpu": "200m", "memory": "512Mi", "storage": "5Gi"},
    "elasticsearch": {"cpu": "500m", "memory": "2Gi", "storage": "10Gi"},
    "kafka":         {"cpu": "500m", "memory": "1Gi", "storage": "10Gi"},
    "mysql":         {"cpu": "500m", "memory": "1Gi", "storage": "10Gi"},
    "postgresql":    {"cpu": "500m", "memory": "1Gi", "storage": "10Gi"},
    "mongodb":       {"cpu": "500m", "memory": "1Gi", "storage": "10Gi"},
}

POLL_INTERVAL = 5      # 秒，对齐前台轮询
POLL_TIMEOUT = 600     # 秒，单实例就绪超时


def log(msg: str):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def smoke_one(engine: str) -> bool:
    name = f"smoke-{engine}-01"
    driver = get_driver(engine)
    payload = {"name": name, "engine_type": engine, **SMOKE_SPECS[engine]}
    spec = spec_for(engine, payload)

    log(f"[{engine}] 建库 {name} ...")
    try:
        driver.create(spec)
    except Exception as e:
        log(f"[{engine}] ❌ 建库失败: {e}")
        return False

    log(f"[{engine}] 轮询状态（超时 {POLL_TIMEOUT}s）...")
    deadline = time.time() + POLL_TIMEOUT
    ok = False
    while time.time() < deadline:
        try:
            st = driver.get(name)["status"]
        except Exception as e:
            log(f"[{engine}] 查状态出错: {e}")
            st = None
        log(f"[{engine}] 当前: {st}")
        if st == status.READY:
            ok = True
            break
        if st == status.ERROR:
            log(f"[{engine}] ❌ 进入 error 状态")
            break
        time.sleep(POLL_INTERVAL)

    if ok:
        try:
            conn = driver.connection(name)
            log(f"[{engine}] ✅ ready，连接信息: {conn.model_dump() if hasattr(conn,'model_dump') else conn}")
        except Exception as e:
            log(f"[{engine}] ⚠️ ready 但取连接失败（可能 Secret 名待确认）: {e}")

    log(f"[{engine}] 清理删除 {name} ...")
    try:
        driver.delete(name)
        log(f"[{engine}] 已删除")
    except Exception as e:
        log(f"[{engine}] ⚠️ 删除失败，需手工清理: {e}")

    return ok


def main():
    engines = sys.argv[1:] or ALL_ENGINES
    results = {}
    for engine in engines:
        if engine not in ALL_ENGINES:
            log(f"跳过未知引擎: {engine}")
            continue
        log(f"===== 冒烟: {engine} =====")
        results[engine] = smoke_one(engine)
        print()

    log("===== 汇总 =====")
    for engine, ok in results.items():
        log(f"  {engine:14} {'✅ PASS' if ok else '❌ FAIL'}")
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
