import StorageIcon from '@mui/icons-material/Storage'
import type { EngineType } from '../api/types'
import { ENGINE_META } from '../config/engines'

// 引擎图标：用 emoji 占位（后续可换真实 logo），统一尺寸。
export default function EngineIcon({ engine, size = 24 }: { engine: EngineType; size?: number }) {
  const meta = ENGINE_META[engine]
  if (!meta) return <StorageIcon sx={{ fontSize: size }} />
  return (
    <span style={{ fontSize: size, lineHeight: 1 }} title={meta.label} aria-label={meta.label}>
      {meta.emoji}
    </span>
  )
}
