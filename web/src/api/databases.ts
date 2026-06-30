import { http } from './client'
import type {
  Connection,
  CreateDatabaseRequest,
  CreateResponse,
  DatabaseInstance,
  DatabaseListItem,
  DeleteResponse,
  EngineInfo,
  EngineType,
} from './types'

// 7 个后端接口的封装（对应后端 app/api/databases.py）

// 引擎及版本
export async function getEngines(): Promise<EngineInfo[]> {
  const { data } = await http.get<{ engines: EngineInfo[] }>('/database-engines')
  return data.engines
}

// 建库（engine_type 在 body）→ 202
export async function createDatabase(
  req: CreateDatabaseRequest,
): Promise<CreateResponse> {
  const { data } = await http.post<CreateResponse>('/databases', req)
  return data
}

// 列某引擎全部实例
export async function listDatabases(
  engineType: EngineType,
): Promise<DatabaseListItem[]> {
  const { data } = await http.get<{ items: DatabaseListItem[] }>(
    `/databases/${engineType}`,
  )
  return data.items
}

// 查单个实例状态
export async function getDatabase(
  engineType: EngineType,
  name: string,
): Promise<DatabaseInstance> {
  const { data } = await http.get<DatabaseInstance>(
    `/databases/${engineType}/${name}`,
  )
  return data
}

// 删除 → 202
export async function deleteDatabase(
  engineType: EngineType,
  name: string,
): Promise<DeleteResponse> {
  const { data } = await http.delete<DeleteResponse>(
    `/databases/${engineType}/${name}`,
  )
  return data
}

// 取连接信息（按 type 判别的连接对象）
export async function getConnection(
  engineType: EngineType,
  name: string,
): Promise<Connection> {
  const { data } = await http.get<Connection>(
    `/databases/${engineType}/${name}/connection`,
  )
  return data
}

// 健康检查
export async function getHealth(): Promise<boolean> {
  try {
    await http.get('/healthz')
    return true
  } catch {
    return false
  }
}
