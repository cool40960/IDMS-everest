import { createTheme } from '@mui/material/styles'

// 配色/风格取自 OpenEverest 开源源码(ui/packages/design)的真实主题，对齐其视觉：
//   主色蓝 #0E5FB5 / dark #0B4A8C；品牌深灰 #3A4151
//   成功 teal #00745B / 错误 #B10810 / 警告 #9C7407
//   字体 Poppins(标题/按钮) + Roboto(正文)；按钮胶囊形；卡片靠边框不靠阴影
export const EVEREST = {
  primary: '#0E5FB5',
  primaryDark: '#0B4A8C',
  primaryLight: '#127be8',
  brand: '#3A4151',
  bg: '#F0F1F4',
  success: '#00745B',
  error: '#B10810',
  warning: '#9C7407',
  border: 'rgba(44,50,62,0.18)', // 卡片/分隔细线
}

const POPPINS = '"Poppins","Roboto","Helvetica","Arial",sans-serif'
const ROBOTO = '"Roboto","Helvetica","Arial",sans-serif'

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: EVEREST.primary, dark: EVEREST.primaryDark, light: EVEREST.primaryLight },
    secondary: { main: EVEREST.brand },
    background: { default: EVEREST.bg, paper: '#FFFFFF' },
    success: { main: EVEREST.success },
    error: { main: EVEREST.error },
    warning: { main: EVEREST.warning },
    info: { main: EVEREST.primary },
    text: { primary: 'rgba(44,50,62,1)', secondary: 'rgba(44,50,62,0.65)' },
    divider: EVEREST.border,
  },
  shape: { borderRadius: 8 },
  typography: {
    fontFamily: ROBOTO,
    h4: { fontFamily: POPPINS, fontWeight: 600 },
    h5: { fontFamily: POPPINS, fontWeight: 600 },
    h6: { fontFamily: POPPINS, fontWeight: 600 },
    subtitle1: { fontFamily: POPPINS, fontWeight: 600 },
    button: { fontFamily: POPPINS, textTransform: 'none', fontWeight: 500 },
  },
  components: {
    MuiButton: {
      defaultProps: { disableElevation: true },
      styleOverrides: { root: { borderRadius: 128 } }, // 胶囊形按钮(Percona 标志)
    },
    // 卡片靠 1px 边框 + 圆角，不用阴影
    MuiPaper: {
      defaultProps: { elevation: 0 },
      styleOverrides: {
        root: { backgroundImage: 'none' },
        outlined: { border: `1px solid ${EVEREST.border}` },
      },
    },
  },
})
