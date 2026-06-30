import Box from '@mui/material/Box'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'
import CheckIcon from '@mui/icons-material/Check'
import PriorityHighIcon from '@mui/icons-material/PriorityHigh'
import AutorenewIcon from '@mui/icons-material/Autorenew'
import type { SvgIconComponent } from '@mui/icons-material'
import type { DbStatus } from '../api/types'
import { STATUS_LABEL } from '../config/engines'

// 仿 OpenEverest status-field：圆形柔色底 + 字形图标 + 文字（8px 间距）。
// 进行中（creating/initializing/deleting）图标转圈动画。
type Kind = 'success' | 'error' | 'pending'

const KIND: Record<DbStatus, Kind> = {
  ready: 'success',
  error: 'error',
  creating: 'pending',
  initializing: 'pending',
  deleting: 'pending',
}

const STYLE: Record<Kind, { bg: string; fg: string; Icon: SvgIconComponent; spin?: boolean }> = {
  success: { bg: '#E7F6F1', fg: '#00745B', Icon: CheckIcon },
  error: { bg: '#FFECE9', fg: '#B10810', Icon: PriorityHighIcon },
  pending: { bg: '#FFF2B2', fg: '#856E00', Icon: AutorenewIcon, spin: true },
}

export default function StatusChip({ status }: { status: DbStatus }) {
  const { bg, fg, Icon, spin } = STYLE[KIND[status]]
  return (
    <Stack direction="row" gap={1} alignItems="center">
      <Box
        sx={{
          width: 20,
          height: 20,
          borderRadius: '10px',
          bgcolor: bg,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
        }}
      >
        <Icon
          sx={{
            fontSize: 13,
            color: fg,
            ...(spin && { animation: 'idms-spin 2s linear infinite' }),
            '@keyframes idms-spin': {
              from: { transform: 'rotate(0deg)' },
              to: { transform: 'rotate(360deg)' },
            },
          }}
        />
      </Box>
      <Typography variant="body2" sx={{ color: 'text.primary' }}>
        {STATUS_LABEL[status]}
      </Typography>
    </Stack>
  )
}
