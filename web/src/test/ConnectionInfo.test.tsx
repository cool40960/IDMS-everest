import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ThemeProvider } from '@mui/material/styles'
import ConnectionInfo from '../components/ConnectionInfo'
import { theme } from '../theme'
import type { Connection } from '../api/types'

function renderConn(conn: Connection) {
  return render(
    <ThemeProvider theme={theme}>
      <ConnectionInfo conn={conn} />
    </ThemeProvider>,
  )
}

describe('ConnectionInfo 按 type 异构渲染', () => {
  it('kafka 显示 bootstrap_servers，无密码字段', () => {
    renderConn({ type: 'kafka', host: 'h', port: 9092, bootstrap_servers: 'h:9092', security: 'PLAINTEXT' })
    expect(screen.getByText('Bootstrap Servers')).toBeInTheDocument()
    expect(screen.getByText('h:9092')).toBeInTheDocument()
    expect(screen.queryByText('密码')).toBeNull()
  })

  it('redis 显示密码 + sentinel', () => {
    renderConn({
      type: 'redis', host: 'h', port: 6379, password: 'secret',
      sentinel: { host: 's', port: 26379, master_name: 'mymaster' },
    })
    expect(screen.getByText('密码')).toBeInTheDocument()
    expect(screen.getByText('Master Name')).toBeInTheDocument()
    expect(screen.getByText('mymaster')).toBeInTheDocument()
  })

  it('elasticsearch 显示 scheme/用户名', () => {
    renderConn({ type: 'elasticsearch', host: 'h', port: 9200, scheme: 'https', username: 'elastic', password: 'p' })
    expect(screen.getByText('协议')).toBeInTheDocument()
    expect(screen.getByText('https')).toBeInTheDocument()
    expect(screen.getByText('elastic')).toBeInTheDocument()
  })

  it('clickhouse 显示 HTTP Port', () => {
    renderConn({ type: 'clickhouse', host: 'h', port: 9000, http_port: 8123, username: 'idms', password: 'p' })
    expect(screen.getByText('HTTP Port')).toBeInTheDocument()
    expect(screen.getByText('8123')).toBeInTheDocument()
  })

  it('mysql 显示标准账密字段', () => {
    renderConn({ type: 'mysql', host: 'h', port: 3306, username: 'root', password: 'p' })
    expect(screen.getByText('用户名')).toBeInTheDocument()
    expect(screen.getByText('root')).toBeInTheDocument()
  })

  it('密码默认遮掩', () => {
    renderConn({ type: 'mysql', host: 'h', port: 3306, username: 'root', password: 'topsecret' })
    expect(screen.queryByText('topsecret')).toBeNull()
    expect(screen.getByText('••••••••')).toBeInTheDocument()
  })
})
