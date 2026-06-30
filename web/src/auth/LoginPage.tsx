import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import Box from '@mui/material/Box'
import Stack from '@mui/material/Stack'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import TextField from '@mui/material/TextField'
import Button from '@mui/material/Button'
import Typography from '@mui/material/Typography'
import StorageIcon from '@mui/icons-material/Storage'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import { useAuth } from './authContext'
import { EVEREST } from '../theme'

// 仿 OpenEverest 登录页：左右两栏。左 35% 品牌栏，右 65% 背景上居中 400px 登录卡。
const LINKS = [
  { label: '加入社区', href: '#' },
  { label: '查看文档', href: '#' },
  { label: '商业支持', href: '#' },
]

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
    <Stack direction="row" sx={{ height: '100vh', overflow: 'hidden' }}>
      {/* 左：品牌栏 */}
      <Stack
        sx={{
          width: '35%',
          minWidth: 360,
          py: 8,
          px: 5,
          bgcolor: '#fff',
          display: { xs: 'none', md: 'flex' },
        }}
      >
        <StorageIcon sx={{ fontSize: 88, color: EVEREST.primary, mb: 3 }} />
        <Typography variant="h4" sx={{ mb: 3, color: 'text.primary' }}>
          欢迎使用 IDMS，一站式云原生数据库管理平台
        </Typography>
        <Typography sx={{ color: 'text.secondary', lineHeight: 1.7 }}>
          IDMS 让你在统一界面上创建和管理 MySQL、PostgreSQL、MongoDB、ClickHouse、
          Redis、Elasticsearch、Kafka 七种数据库，背后由各 Operator 真正执行，
          省去逐个数据库的运维负担。现在就创建你的第一个数据库实例吧。
        </Typography>
        <Stack sx={{ mt: 'auto' }} alignItems="flex-start" gap={1}>
          {LINKS.map((l) => (
            <Button
              key={l.label}
              href={l.href}
              startIcon={<ArrowForwardIcon />}
              sx={{ color: EVEREST.primary }}
            >
              {l.label}
            </Button>
          ))}
        </Stack>
      </Stack>

      {/* 右：背景 + 居中登录卡 */}
      <Box
        sx={{
          flexGrow: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: `linear-gradient(135deg, ${EVEREST.primary} 0%, #0b3a6e 60%, ${EVEREST.brand} 100%)`,
        }}
      >
        <Card elevation={6} sx={{ width: 400, py: 1, px: 3 }}>
          <CardContent>
            <Stack alignItems="center">
              <Typography variant="h6" sx={{ mb: 3 }}>
                登录
              </Typography>
              <Typography variant="caption" sx={{ mb: 2, color: 'text.secondary' }}>
                输入用户名和密码以登录。
              </Typography>
              <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
                <TextField
                  label="用户名"
                  fullWidth
                  sx={{ mb: 2 }}
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  autoFocus
                />
                <TextField
                  label="密码"
                  type="password"
                  fullWidth
                  sx={{ mb: 2 }}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <Button type="submit" variant="contained" fullWidth sx={{ mb: 1 }}>
                  登录
                </Button>
              </Box>
              <Typography variant="caption" sx={{ mt: 1, color: 'text.disabled' }}>
                本轮为演示登录，填用户名即可进入
              </Typography>
            </Stack>
          </CardContent>
        </Card>
      </Box>
    </Stack>
  )
}
