import { useState } from 'react'
import Box from '@mui/material/Box'
import Typography from '@mui/material/Typography'
import IconButton from '@mui/material/IconButton'
import Table from '@mui/material/Table'
import TableBody from '@mui/material/TableBody'
import TableCell from '@mui/material/TableCell'
import TableRow from '@mui/material/TableRow'
import VisibilityIcon from '@mui/icons-material/Visibility'
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff'
import ContentCopyIcon from '@mui/icons-material/ContentCopy'
import type { Connection } from '../api/types'

function Row({ label, value, secret }: { label: string; value: string; secret?: boolean }) {
  const [show, setShow] = useState(false)
  const display = secret && !show ? '••••••••' : value
  return (
    <TableRow>
      <TableCell sx={{ width: 160, color: 'text.secondary' }}>{label}</TableCell>
      <TableCell>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, fontFamily: 'monospace' }}>
          {display}
          {secret && (
            <IconButton size="small" onClick={() => setShow((s) => !s)}>
              {show ? <VisibilityOffIcon fontSize="inherit" /> : <VisibilityIcon fontSize="inherit" />}
            </IconButton>
          )}
          <IconButton size="small" onClick={() => navigator.clipboard?.writeText(value)}>
            <ContentCopyIcon fontSize="inherit" />
          </IconButton>
        </Box>
      </TableCell>
    </TableRow>
  )
}

// 按连接对象的 type 分支渲染（异构：Kafka 无账密、Redis 有 sentinel、ES 有 scheme）
export default function ConnectionInfo({ conn }: { conn: Connection }) {
  const rows: { label: string; value: string; secret?: boolean }[] = []

  if (conn.type === 'kafka') {
    rows.push({ label: 'Bootstrap Servers', value: conn.bootstrap_servers })
    rows.push({ label: '安全协议', value: conn.security })
  } else if (conn.type === 'redis') {
    rows.push({ label: 'Host', value: conn.host })
    rows.push({ label: 'Port', value: String(conn.port) })
    rows.push({ label: '密码', value: conn.password, secret: true })
    if (conn.sentinel) {
      rows.push({ label: 'Sentinel Host', value: conn.sentinel.host })
      rows.push({ label: 'Sentinel Port', value: String(conn.sentinel.port) })
      rows.push({ label: 'Master Name', value: conn.sentinel.master_name })
    }
  } else if (conn.type === 'elasticsearch') {
    rows.push({ label: 'Host', value: conn.host })
    rows.push({ label: 'Port', value: String(conn.port) })
    rows.push({ label: '协议', value: conn.scheme })
    rows.push({ label: '用户名', value: conn.username })
    rows.push({ label: '密码', value: conn.password, secret: true })
    if (conn.ca_cert) rows.push({ label: 'CA 证书', value: conn.ca_cert })
  } else if (conn.type === 'clickhouse') {
    rows.push({ label: 'Host', value: conn.host })
    rows.push({ label: 'Port (native)', value: String(conn.port) })
    rows.push({ label: 'HTTP Port', value: String(conn.http_port) })
    rows.push({ label: '用户名', value: conn.username })
    rows.push({ label: '密码', value: conn.password, secret: true })
  } else {
    // mysql / postgresql / mongodb
    rows.push({ label: 'Host', value: conn.host })
    rows.push({ label: 'Port', value: String(conn.port) })
    rows.push({ label: '用户名', value: conn.username })
    rows.push({ label: '密码', value: conn.password, secret: true })
  }

  return (
    <Box>
      <Typography variant="subtitle1" sx={{ mb: 1 }}>
        连接信息（{conn.type}）
      </Typography>
      <Table size="small">
        <TableBody>
          {rows.map((r) => (
            <Row key={r.label} {...r} />
          ))}
        </TableBody>
      </Table>
    </Box>
  )
}
