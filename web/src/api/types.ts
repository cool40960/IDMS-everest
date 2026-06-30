// 与 IDMS 后端严格对齐的 TS 类型（后端 app/models/specs.py、connection.py）

// 7 种引擎
export type EngineType =
  | 'mysql'
  | 'postgresql'
  | 'mongodb'
  | 'clickhouse'
  | 'redis'
  | 'elasticsearch'
  | 'kafka'

// 统一状态词（后端 app/core/status.py）—— 注意是 error 不是 failed
export type DbStatus =
  | 'creating'
  | 'initializing'
  | 'ready'
  | 'error'
  | 'deleting'

// 建库请求体（engine_type 在 body）。shards 仅 ClickHouse 用
export interface CreateDatabaseRequest {
  name: string
  engine_type: EngineType
  cpu: string
  memory: string
  storage: string
  replicas?: number
  shards?: number
}

// 建库 202 / 删除 202 响应
export interface CreateResponse {
  name: string
  engine_type: EngineType
  status: DbStatus
}
export interface DeleteResponse {
  name: string
  status: DbStatus
}

// 查单个实例
export interface DatabaseInstance {
  name: string
  engine_type: EngineType
  status: DbStatus
  message?: string
  raw?: unknown
}

// 列表项（GET /databases/{engine_type}）
export interface DatabaseListItem {
  name: string
  engine_type: EngineType
  status: DbStatus
}

// 引擎及版本（GET /database-engines）
export interface EngineInfo {
  engine_type: EngineType
  versions: string[]
}

// ---- 连接对象（带 type 判别，后端 connection.py，异构）----
export interface SentinelInfo {
  host: string
  port: number
  master_name: string
}

export interface MySQLConnection {
  type: 'mysql'
  host: string
  port: number
  username: string
  password: string
}
export interface PostgreSQLConnection {
  type: 'postgresql'
  host: string
  port: number
  username: string
  password: string
}
export interface MongoDBConnection {
  type: 'mongodb'
  host: string
  port: number
  username: string
  password: string
}
export interface ClickHouseConnection {
  type: 'clickhouse'
  host: string
  port: number
  username: string
  password: string
  http_port: number
}
export interface ElasticsearchConnection {
  type: 'elasticsearch'
  host: string
  port: number
  scheme: string
  username: string
  password: string
  ca_cert?: string | null
}
export interface KafkaConnection {
  type: 'kafka'
  host: string
  port: number
  bootstrap_servers: string
  security: string
}
export interface RedisConnection {
  type: 'redis'
  host: string
  port: number
  password: string
  sentinel?: SentinelInfo | null
}

// 判别联合：按 type 区分
export type Connection =
  | MySQLConnection
  | PostgreSQLConnection
  | MongoDBConnection
  | ClickHouseConnection
  | ElasticsearchConnection
  | KafkaConnection
  | RedisConnection

// 后端统一错误格式
export interface ApiError {
  error: string
}
