import Chip from '@mui/material/Chip'
import CircularProgress from '@mui/material/CircularProgress'
import type { DbStatus } from '../api/types'
import { STATUS_COLOR, STATUS_LABEL } from '../config/engines'

// 状态彩色标签。creating/initializing/deleting 带转圈动效表示进行中。
export default function StatusChip({ status }: { status: DbStatus }) {
  const inProgress = status === 'creating' || status === 'initializing' || status === 'deleting'
  return (
    <Chip
      size="small"
      color={STATUS_COLOR[status]}
      variant={status === 'ready' || status === 'error' ? 'filled' : 'outlined'}
      icon={inProgress ? <CircularProgress size={12} thickness={6} /> : undefined}
      label={STATUS_LABEL[status]}
    />
  )
}
