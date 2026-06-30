import {
  SiMysql,
  SiPostgresql,
  SiMongodb,
  SiRedis,
  SiElasticsearch,
  SiApachekafka,
  SiClickhouse,
} from 'react-icons/si'
import type { IconType } from 'react-icons'
import type { EngineType } from '../api/types'

// 各引擎真实品牌 logo + 官方品牌色（替换之前的 emoji，专业感对齐 OpenEverest）
const LOGO: Record<EngineType, { Icon: IconType; color: string }> = {
  mysql: { Icon: SiMysql, color: '#4479A1' },
  postgresql: { Icon: SiPostgresql, color: '#4169E1' },
  mongodb: { Icon: SiMongodb, color: '#47A248' },
  redis: { Icon: SiRedis, color: '#FF4438' },
  elasticsearch: { Icon: SiElasticsearch, color: '#005571' },
  kafka: { Icon: SiApachekafka, color: '#231F20' },
  clickhouse: { Icon: SiClickhouse, color: '#E6B800' },
}

export default function EngineIcon({ engine, size = 22 }: { engine: EngineType; size?: number }) {
  const item = LOGO[engine]
  if (!item) return null
  const { Icon, color } = item
  return <Icon size={size} color={color} style={{ display: 'block', flexShrink: 0 }} />
}
