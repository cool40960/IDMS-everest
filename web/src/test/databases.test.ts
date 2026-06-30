import { describe, it, expect, vi, beforeEach } from 'vitest'
import { http } from '../api/client'
import * as api from '../api/databases'

// mock axios 实例的方法
vi.mock('../api/client', async () => {
  const actual = await vi.importActual<typeof import('../api/client')>('../api/client')
  return {
    ...actual,
    http: {
      get: vi.fn(),
      post: vi.fn(),
      delete: vi.fn(),
    },
  }
})

const mockHttp = http as unknown as {
  get: ReturnType<typeof vi.fn>
  post: ReturnType<typeof vi.fn>
  delete: ReturnType<typeof vi.fn>
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('databases API 封装', () => {
  it('getEngines 调对路径并解出 engines', async () => {
    mockHttp.get.mockResolvedValue({ data: { engines: [{ engine_type: 'redis', versions: ['7'] }] } })
    const r = await api.getEngines()
    expect(mockHttp.get).toHaveBeenCalledWith('/database-engines')
    expect(r[0].engine_type).toBe('redis')
  })

  it('createDatabase POST /databases 带 body', async () => {
    mockHttp.post.mockResolvedValue({ data: { name: 'ck-01', engine_type: 'clickhouse', status: 'creating' } })
    const r = await api.createDatabase({
      name: 'ck-01', engine_type: 'clickhouse', cpu: '1', memory: '2Gi', storage: '50Gi', shards: 1,
    })
    expect(mockHttp.post).toHaveBeenCalledWith('/databases', expect.objectContaining({ engine_type: 'clickhouse' }))
    expect(r.status).toBe('creating')
  })

  it('listDatabases GET /databases/{engine}', async () => {
    mockHttp.get.mockResolvedValue({ data: { items: [{ name: 'a', engine_type: 'redis', status: 'ready' }] } })
    const r = await api.listDatabases('redis')
    expect(mockHttp.get).toHaveBeenCalledWith('/databases/redis')
    expect(r).toHaveLength(1)
  })

  it('getDatabase GET /databases/{engine}/{name}', async () => {
    mockHttp.get.mockResolvedValue({ data: { name: 'a', engine_type: 'redis', status: 'ready' } })
    await api.getDatabase('redis', 'a')
    expect(mockHttp.get).toHaveBeenCalledWith('/databases/redis/a')
  })

  it('deleteDatabase DELETE /databases/{engine}/{name}', async () => {
    mockHttp.delete.mockResolvedValue({ data: { name: 'a', status: 'deleting' } })
    const r = await api.deleteDatabase('kafka', 'k1')
    expect(mockHttp.delete).toHaveBeenCalledWith('/databases/kafka/k1')
    expect(r.status).toBe('deleting')
  })

  it('getConnection GET .../connection', async () => {
    mockHttp.get.mockResolvedValue({ data: { type: 'kafka', host: 'h', port: 9092, bootstrap_servers: 'h:9092', security: 'PLAINTEXT' } })
    const r = await api.getConnection('kafka', 'k1')
    expect(mockHttp.get).toHaveBeenCalledWith('/databases/kafka/k1/connection')
    expect(r.type).toBe('kafka')
  })

  it('getHealth 失败时返回 false', async () => {
    mockHttp.get.mockRejectedValue(new Error('boom'))
    expect(await api.getHealth()).toBe(false)
  })
})
