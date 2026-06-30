import { createTheme } from '@mui/material/styles'

// 仿 OpenEverest 的视觉风格：紫色主色 + 浅灰背景 + Material 风格。
export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#2C2D5B' }, // 深靛蓝，仿 Everest 顶栏
    secondary: { main: '#7C4DFF' },
    background: { default: '#F5F6FA', paper: '#FFFFFF' },
    success: { main: '#2E7D32' },
    error: { main: '#C62828' },
    warning: { main: '#ED6C02' },
    info: { main: '#0288D1' },
  },
  shape: { borderRadius: 8 },
  typography: {
    fontFamily: '"Roboto","Helvetica","Arial",sans-serif',
    h5: { fontWeight: 600 },
    h6: { fontWeight: 600 },
  },
  components: {
    MuiButton: { defaultProps: { disableElevation: true } },
  },
})
