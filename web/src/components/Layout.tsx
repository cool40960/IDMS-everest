import { type ReactNode } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import AppBar from '@mui/material/AppBar'
import Toolbar from '@mui/material/Toolbar'
import Typography from '@mui/material/Typography'
import Box from '@mui/material/Box'
import Drawer from '@mui/material/Drawer'
import List from '@mui/material/List'
import ListItemButton from '@mui/material/ListItemButton'
import ListItemIcon from '@mui/material/ListItemIcon'
import ListItemText from '@mui/material/ListItemText'
import Button from '@mui/material/Button'
import StorageIcon from '@mui/icons-material/Storage'
import AddIcon from '@mui/icons-material/Add'
import LogoutIcon from '@mui/icons-material/Logout'
import PersonOutlineIcon from '@mui/icons-material/PersonOutline'
import { useAuth } from '../auth/authContext'
import { EVEREST } from '../theme'

const DRAWER_WIDTH = 220

// 仿 OpenEverest 浅色布局：白色顶栏(底部细线) + 白色侧栏(选中项蓝色高亮) + 浅灰主区。
export default function Layout({ children }: { children: ReactNode }) {
  const navigate = useNavigate()
  const location = useLocation()
  const { logout, username } = useAuth()

  const navItems = [
    { label: '数据库', icon: <StorageIcon />, path: '/databases' },
    { label: '创建实例', icon: <AddIcon />, path: '/databases/new' },
  ]

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <AppBar
        position="fixed"
        elevation={0}
        sx={{
          zIndex: (t) => t.zIndex.drawer + 1,
          bgcolor: '#fff',
          color: 'text.primary',
          borderBottom: `1px solid ${EVEREST.border}`,
        }}
      >
        <Toolbar>
          <Box sx={{ width: DRAWER_WIDTH - 16, display: 'flex', alignItems: 'center' }}>
            <StorageIcon sx={{ mr: 1, color: EVEREST.primary }} />
            <Typography variant="h6" sx={{ fontWeight: 700, color: EVEREST.primary }}>
              IDMS
            </Typography>
          </Box>
          <Typography variant="body2" sx={{ flexGrow: 1, color: 'text.secondary' }}>
            数据库管理平台
          </Typography>
          <PersonOutlineIcon sx={{ color: 'text.secondary', mr: 0.5 }} fontSize="small" />
          <Typography variant="body2" sx={{ mr: 2, color: 'text.secondary' }}>
            {username}
          </Typography>
          <Button color="inherit" size="small" startIcon={<LogoutIcon />} onClick={logout}>
            退出
          </Button>
        </Toolbar>
      </AppBar>

      <Drawer
        variant="permanent"
        sx={{
          width: DRAWER_WIDTH,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: {
            width: DRAWER_WIDTH,
            boxSizing: 'border-box',
            bgcolor: '#fff',
            borderRight: `1px solid ${EVEREST.border}`,
          },
        }}
      >
        <Toolbar />
        <List sx={{ px: 1, pt: 1.5 }}>
          {navItems.map((item) => {
            const selected = location.pathname === item.path
            return (
              <ListItemButton
                key={item.path}
                selected={selected}
                onClick={() => navigate(item.path)}
                sx={{
                  borderRadius: 2,
                  mb: 0.5,
                  '&.Mui-selected': {
                    bgcolor: 'rgba(14,95,181,0.10)',
                    color: EVEREST.primary,
                    '& .MuiListItemIcon-root': { color: EVEREST.primary },
                    '&:hover': { bgcolor: 'rgba(14,95,181,0.16)' },
                  },
                }}
              >
                <ListItemIcon sx={{ minWidth: 38 }}>{item.icon}</ListItemIcon>
                <ListItemText primary={item.label} primaryTypographyProps={{ fontWeight: selected ? 600 : 400 }} />
              </ListItemButton>
            )
          })}
        </List>
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1, p: 4, bgcolor: 'background.default', minHeight: '100vh' }}>
        <Toolbar />
        {children}
      </Box>
    </Box>
  )
}
