import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ThemeProvider } from '@mui/material/styles'
import StatusChip from '../components/StatusChip'
import { theme } from '../theme'
import { STATUS_LABEL, STATUS_COLOR } from '../config/engines'

function renderChip(status: Parameters<typeof StatusChip>[0]['status']) {
  return render(
    <ThemeProvider theme={theme}>
      <StatusChip status={status} />
    </ThemeProvider>,
  )
}

describe('StatusChip', () => {
  it('ready 显示就绪标签', () => {
    renderChip('ready')
    expect(screen.getByText('就绪')).toBeInTheDocument()
  })

  it('error 显示错误标签', () => {
    renderChip('error')
    expect(screen.getByText('错误')).toBeInTheDocument()
  })

  it('五个状态都有中文标签和颜色映射', () => {
    const statuses = ['creating', 'initializing', 'ready', 'error', 'deleting'] as const
    for (const s of statuses) {
      expect(STATUS_LABEL[s]).toBeTruthy()
      expect(STATUS_COLOR[s]).toBeTruthy()
    }
  })
})
