# IDMS 后端

OpenEverest 产品化封装的统一数据库管理后端。对外暴露**一套 HTTP 接口**，
内部按 `engine_type` 自动分流到两条路径，前台无感：

- **路径一**（mysql / postgresql / mongodb）→ 调 OpenEverest REST API（:8080）
- **路径二**（clickhouse / redis / elasticsearch / kafka）→ 直接写 K8s CRD（:6443）

详见设计文档：`docs/superpowers/specs/2026-06-29-idms-python-backend-design.md`。

## 目录结构

```
app/
├── main.py            # FastAPI 入口 + 异常处理器
├── registry.py        # engine_type → driver 查表
├── api/databases.py   # 7 个 HTTP 接口
├── models/            # specs(参数校验) + connection(连接对象)
├── drivers/           # base 抽象类 + k8s_base 中间类 + 5 个驱动
└── core/              # k8s_client / errors / status
tests/                 # 单元测试（全 mock，不碰集群）
smoke.py               # 端到端冒烟（手动连真集群）
```

## 安装

本机已有 venv（Python 3.11）。重建：

```bash
python3.11 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## 跑测试

```bash
.venv/bin/python -m pytest -q
```

## 起服务

```bash
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8080
```

Swagger 文档：`http://<host>:8080/docs`（前台据此对接，能看到每个接口的参数和返回）。

> 注意：本机配了 HTTP 代理，本地 curl 自测需加 `--noproxy '*'`，否则请求会走代理拿不到响应。

## 环境变量

| 变量 | 说明 |
|---|---|
| `EVEREST_USER` | OpenEverest 登录用户名（路径一必需，不硬编码） |
| `EVEREST_PASSWORD` | OpenEverest 登录密码 |
| `EVEREST_HOST` | 可选，默认 `http://10.10.214.193:8080` |

## HTTP 接口

| 动作 | 方法 + 路径 |
|---|---|
| 建库 | `POST /databases`（engine_type 在 body） |
| 查单个 | `GET /databases/{engine_type}/{name}` |
| 列同类 | `GET /databases/{engine_type}` |
| 删库 | `DELETE /databases/{engine_type}/{name}` |
| 取连接 | `GET /databases/{engine_type}/{name}/connection` |
| 引擎列表 | `GET /database-engines` |
| 健康检查 | `GET /healthz` |

建库/删库返回 `202`（异步：写完 CRD 即返回，Pod 还在起，前台轮询状态）。
统一状态词：`creating / initializing / ready / error / deleting`。

## 运行方式

线上部署为**集群内 Pod**，用 `load_incluster_config`（无需 kubeconfig）。
本地开发自动回退 `/etc/kubernetes/admin.conf`。

## 待办（留到冒烟阶段连集群确认）

- Redis / Elasticsearch 连接密码的 Secret 名（代码中标 `TODO-confirm-secret`）
- redis-operator 建议锁定固定版本（实测为 `:latest`，`rfr-`/`rfs-` 命名契约随版本可能变化）
