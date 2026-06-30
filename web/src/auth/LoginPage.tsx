import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import Box from '@mui/material/Box'
import Paper from '@mui/material/Paper'
import TextField from '@mui/material/TextField'
import Button from '@mui/material/Button'
import Typography from '@mui/material/Typography'
import StorageIcon from '@mui/icons-material/Storage'
import { useAuth } from './authContext'

// 登录页外壳。本轮不接真实认证：填了用户名即登录成功进主界面。
export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('')

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (!username.trim()) return
    login(username.trim())
    navigate('/databases')
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'background.default',
      }}
    >
      <Paper elevation={3} sx={{ p: 4, width: 360 }}>
        <Box sx={{ textAlign: 'center', mb: 3 }}>
          <StorageIcon color="primary" sx={{ fontSize: 48 }} />
          <Typography variant="h5" sx={{ mt: 1 }}>
            IDMS
          </Typography>
          <Typography variant="body2" color="text.secondary">
            数据库管理平台
          </Typography>
        </Box>
        <form onSubmit={handleSubmit}>
          <TextField
            label="用户名"
            fullWidth
            margin="normal"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoFocus
          />
          <TextField
            label="密码"
            type="password"
            fullWidth
            margin="normal"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <Button type="submit" variant="contained" fullWidth sx={{ mt: 3 }} size="large">
            登录
          </Button>
        </form>
      </Paper>
    </Box>
  )
}
