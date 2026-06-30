import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import Box from '@mui/material/Box'
import Paper from '@mui/material/Paper'
import Typography from '@mui/material/Typography'
import Button from '@mui/material/Button'
import Divider from '@mui/material/Divider'
import TextField from '@mui/material/TextField'
import CircularProgress from '@mui/material/CircularProgress'
import Alert from '@mui/material/Alert'
import Dialog from '@mui/material/Dialog'
import DialogTitle from '@mui/material/DialogTitle'
import DialogContent from '@mui/material/DialogContent'
import DialogActions from '@mui/material/DialogActions'
import DialogContentText from '@mui/material/DialogContentText'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import DeleteIcon from '@mui/icons-material/Delete'
import type { EngineType } from '../api/types'
import { getDatabase, getConnection, deleteDatabase } from '../api/databases'
import { ENGINE_META } from '../config/engines'
import EngineIcon from '../components/EngineIcon'
import StatusChip from '../components/StatusChip'
import ConnectionInfo from '../components/ConnectionInfo'

export default function DatabaseDetailPage() {
  const { engineType, name } = useParams<{ engineType: EngineType; name: string }>()
  const navigate = useNavigate()
  const [confirmOpen, setConfirmOpen] = useState(false)
  const [confirmInput, setConfirmInput] = useState('') // 删除二次确认：须输入库名

  const detail = useQuery({
    queryKey: ['database', engineType, name],
    queryFn: () => getDatabase(engineType!, name!),
    refetchInterval: 5000,
    enabled: !!engineType && !!name,
  })

  const isReady = detail.data?.status === 'ready'
  const conn = useQuery({
    queryKey: ['connection', engineType, name],
    queryFn: () => getConnection(engineType!, name!),
    enabled: isReady, // 仅 ready 时取连接
    retry: false,
  })

  const del = useMutation({
    mutationFn: () => deleteDatabase(engineType!, name!),
    onSuccess: () => navigate('/databases'),
  })

  const closeConfirm = () => {
    setConfirmOpen(false)
    setConfirmInput('')
  }

  return (
    <Box>
      <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/databases')} sx={{ mb: 2 }}>
        返回列表
      </Button>

      <Paper variant="outlined" sx={{ p: 3, maxWidth: 720 }}>
        {detail.isLoading ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : detail.isError ? (
          <Alert severity="error">{(detail.error as Error)?.message}</Alert>
        ) : (
          <>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
              <EngineIcon engine={engineType!} size={32} />
              <Box sx={{ flexGrow: 1 }}>
                <Typography variant="h5">{name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {ENGINE_META[engineType!]?.label}
                </Typography>
              </Box>
              <StatusChip status={detail.data!.status} />
            </Box>

            {detail.data!.message && (
              <Alert severity={detail.data!.status === 'error' ? 'error' : 'info'} sx={{ mb: 2 }}>
                {detail.data!.message}
              </Alert>
            )}

            <Divider sx={{ my: 2 }} />

            {isReady ? (
              conn.isLoading ? (
                <CircularProgress size={20} />
              ) : conn.isError ? (
                <Alert severity="warning">
                  连接信息暂不可用：{(conn.error as Error)?.message}
                </Alert>
              ) : conn.data ? (
                <ConnectionInfo conn={conn.data} />
              ) : null
            ) : (
              <Typography variant="body2" color="text.secondary">
                实例就绪后显示连接信息（当前：{detail.data!.status}）
              </Typography>
            )}

            <Divider sx={{ my: 2 }} />

            <Button
              color="error"
              variant="outlined"
              startIcon={<DeleteIcon />}
              onClick={() => setConfirmOpen(true)}
            >
              删除实例
            </Button>
          </>
        )}
      </Paper>

      <Dialog open={confirmOpen} onClose={closeConfirm} maxWidth="xs" fullWidth>
        <DialogTitle>删除数据库</DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 1 }}>
            确定要永久删除 <b>{name}</b> 吗？此操作不可恢复。
          </DialogContentText>
          <Alert severity="error" variant="outlined" sx={{ mb: 2 }}>
            不可逆操作：删除后实例和数据将无法找回。
          </Alert>
          <DialogContentText sx={{ mb: 1 }}>
            请输入数据库名称以确认：
          </DialogContentText>
          <TextField
            fullWidth
            size="small"
            placeholder={name}
            value={confirmInput}
            onChange={(e) => setConfirmInput(e.target.value)}
            autoFocus
          />
          {del.isError && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {(del.error as Error)?.message ?? '删除失败'}
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={closeConfirm}>取消</Button>
          <Button
            color="error"
            variant="contained"
            onClick={() => del.mutate()}
            disabled={del.isPending || confirmInput !== name}
          >
            {del.isPending ? '删除中…' : '删除'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
