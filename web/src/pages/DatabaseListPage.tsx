import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import Box from '@mui/material/Box'
import Typography from '@mui/material/Typography'
import Button from '@mui/material/Button'
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup'
import ToggleButton from '@mui/material/ToggleButton'
import Table from '@mui/material/Table'
import TableBody from '@mui/material/TableBody'
import TableCell from '@mui/material/TableCell'
import TableHead from '@mui/material/TableHead'
import TableRow from '@mui/material/TableRow'
import Paper from '@mui/material/Paper'
import IconButton from '@mui/material/IconButton'
import CircularProgress from '@mui/material/CircularProgress'
import Alert from '@mui/material/Alert'
import AddIcon from '@mui/icons-material/Add'
import VisibilityIcon from '@mui/icons-material/Visibility'
import RefreshIcon from '@mui/icons-material/Refresh'
import type { EngineType } from '../api/types'
import { listDatabases } from '../api/databases'
import { ENGINE_LIST } from '../config/engines'
import EngineIcon from '../components/EngineIcon'
import StatusChip from '../components/StatusChip'

export default function DatabaseListPage() {
  const navigate = useNavigate()
  const [engine, setEngine] = useState<EngineType>('clickhouse')

  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['databases', engine],
    queryFn: () => listDatabases(engine),
    refetchInterval: 5000, // 每 5 秒轮询，对齐 OpenEverest
  })

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5" sx={{ flexGrow: 1 }}>
          数据库实例
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => navigate('/databases/new')}
        >
          创建实例
        </Button>
      </Box>

      <ToggleButtonGroup
        value={engine}
        exclusive
        size="small"
        onChange={(_, v) => v && setEngine(v)}
        sx={{ mb: 2, flexWrap: 'wrap' }}
      >
        {ENGINE_LIST.map((m) => (
          <ToggleButton key={m.engine_type} value={m.engine_type}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <EngineIcon engine={m.engine_type} size={18} />
              {m.label}
            </Box>
          </ToggleButton>
        ))}
      </ToggleButtonGroup>

      <Paper variant="outlined">
        <Box sx={{ display: 'flex', alignItems: 'center', px: 2, py: 1 }}>
          <Typography variant="subtitle2" sx={{ flexGrow: 1 }}>
            {ENGINE_LIST.find((m) => m.engine_type === engine)?.label} 实例
            {isFetching && <CircularProgress size={14} sx={{ ml: 1 }} />}
          </Typography>
          <IconButton size="small" onClick={() => refetch()}>
            <RefreshIcon fontSize="small" />
          </IconButton>
        </Box>

        {isError && (
          <Alert severity="error" sx={{ m: 2 }}>
            {(error as Error)?.message ?? '加载失败'}
          </Alert>
        )}

        {isLoading ? (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <CircularProgress />
          </Box>
        ) : (
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>名称</TableCell>
                <TableCell>引擎</TableCell>
                <TableCell>状态</TableCell>
                <TableCell align="right">操作</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {(data ?? []).length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4} align="center" sx={{ py: 4, color: 'text.secondary' }}>
                    暂无实例，点击右上角「创建实例」
                  </TableCell>
                </TableRow>
              ) : (
                data!.map((row) => (
                  <TableRow key={row.name} hover>
                    <TableCell>{row.name}</TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <EngineIcon engine={row.engine_type} size={18} />
                        {row.engine_type}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <StatusChip status={row.status} />
                    </TableCell>
                    <TableCell align="right">
                      <IconButton
                        size="small"
                        onClick={() => navigate(`/databases/${row.engine_type}/${row.name}`)}
                      >
                        <VisibilityIcon fontSize="small" />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        )}
      </Paper>
    </Box>
  )
}
