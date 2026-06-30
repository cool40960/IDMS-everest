import type { EngineType, DbStatus } from '../api/types'

// 状态 → MUI 颜色 / 中文标签
export const STATUS_COLOR: Record<DbStatus, 'success' | 'error' | 'warning' | 'default' | 'info'> = {
  ready: 'success',
  error: 'error',
  creating: 'warning',
  initializing: 'info',
  deleting: 'default',
}

export const STATUS_LABEL: Record<DbStatus, string> = {
  ready: '就绪',
  error: '错误',
  creating: '创建中',
  initializing: '初始化中',
  deleting: '删除中',
}

// 引擎元数据：显示名、图标、所属路径、特有字段
export interface EngineMeta {
  engine_type: EngineType
  label: string // 显示名
  emoji: string // 占位图标
  path: 'everest' | 'k8s' // 走哪条后端路径（仅用于前端分组展示）
  hasShards: boolean // 是否有 shards 字段（仅 ClickHouse）
}

export const ENGINE_META: Record<EngineType, EngineMeta> = {
  mysql: { engine_type: 'mysql', label: 'MySQL', emoji: '🐬', path: 'everest', hasShards: false },
  postgresql: { engine_type: 'postgresql', label: 'PostgreSQL', emoji: '🐘', path: 'everest', hasShards: false },
  mongodb: { engine_type: 'mongodb', label: 'MongoDB', emoji: '🍃', path: 'everest', hasShards: false },
  clickhouse: { engine_type: 'clickhouse', label: 'ClickHouse', emoji: '📊', path: 'k8s', hasShards: true },
  redis: { engine_type: 'redis', label: 'Redis', emoji: '🔴', path: 'k8s', hasShards: false },
  elasticsearch: { engine_type: 'elasticsearch', label: 'Elasticsearch', emoji: '🔍', path: 'k8s', hasShards: false },
  kafka: { engine_type: 'kafka', label: 'Kafka', emoji: '📨', path: 'k8s', hasShards: false },
}

// 有序的引擎列表（用于下拉、导航）
export const ENGINE_LIST: EngineMeta[] = [
  ENGINE_META.mysql,
  ENGINE_META.postgresql,
  ENGINE_META.mongodb,
  ENGINE_META.clickhouse,
  ENGINE_META.redis,
  ENGINE_META.elasticsearch,
  ENGINE_META.kafka,
]
