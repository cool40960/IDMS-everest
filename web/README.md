# IDMS 前端

IDMS 数据库管理平台的 Web 前端，神似 OpenEverest，对接 [IDMS 后端](..)的统一 7 引擎接口。

支持 MySQL / PostgreSQL / MongoDB / ClickHouse / Redis / Elasticsearch / Kafka 七种引擎的
完整生命周期：建库 → 实例列表（状态轮询）→ 查看连接信息 → 删除。

## 技术栈

React 18 + TypeScript + Vite 5 + MUI 5（与 OpenEverest 同款）+ TanStack Query（状态轮询）
+ React Hook Form + Zod（表单校验）+ axios。

## 目录结构

```
src/
├── api/         # 后端接口封装(types/client/databases)
├── auth/        # 登录页 + 登录态
├── components/  # Layout / StatusChip / EngineIcon / ConnectionInfo
├── config/      # engines.ts 引擎元数据(加引擎只改这里)
├── pages/       # 列表 / 建库 / 详情
├── theme.ts     # 仿 OpenEverest 主题
└── App.tsx      # 路由 + 登录守卫
```

## 开发

```bash
npm install
npm run dev      # 起 dev server，默认 http://localhost:5173
npm test         # Vitest 单元测试
npm run build    # 生产构建到 dist/
```

### 连后端（关键）

前端 dev server 通过 Vite proxy 把 `/api/*` 转发到后端 `http://localhost:8080`（绕开跨域）。
**所以开发时后端必须先在 8080 起好**，且带齐连集群的环境变量：

```bash
cd ..
export KUBECONFIG=/tmp/idms-kubeconfig.yaml          # 集群 kubeconfig（从 master 拉）
export EVEREST_USER=admin EVEREST_PASSWORD=admin123  # everest 账密
export NO_PROXY="10.10.214.193,10.10.214.0/24,localhost,127.0.0.1"  # 内网绕开 HTTP 代理
.venv/bin/uvicorn app.main:app --port 8080
```

> 注意：本机有 HTTP 代理，访问内网集群/本地服务都要设 `NO_PROXY`，否则连不上。
> 本机 curl 自测同理要加 `--noproxy '*'`。

### 改后端地址

默认走 `/api`（dev proxy）。生产同源部署可设环境变量 `VITE_API_BASE=''`，或改 `vite.config.ts` 的 proxy target。

## 与后端的契约

- 状态词：`creating / initializing / ready / error / deleting`（彩色 Chip 显示）
- 建库参数：name / cpu / memory / storage / replicas，ClickHouse 额外 shards
- 前端校验规则与后端 Pydantic 对齐（name/cpu/memory/storage 正则一致）
- 连接信息按引擎 type 异构渲染：Kafka 无账密、Redis 有 sentinel、ES 走 https

## 登录

本轮登录页为**外壳**，不接真实认证（后端这轮无鉴权）：填用户名即进主界面。
将来后端做鉴权时，改 `src/auth/authContext.tsx` 与 `src/api/client.ts` 的 token 注入即可。
