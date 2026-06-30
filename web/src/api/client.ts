import axios, { AxiosError } from 'axios'
import type { ApiError } from './types'

// 后端基址：开发期走 Vite proxy 的 /api（同源，绕开 CORS）。
// 可用 VITE_API_BASE 覆盖（如生产同源部署设为 ''）。
const baseURL = import.meta.env.VITE_API_BASE ?? '/api'

export const http = axios.create({ baseURL, timeout: 15000 })

// 统一错误：把后端 {"error": "..."} 抽成可读 message 抛出
export class IdmsApiError extends Error {
  status: number
  constructor(message: string, status: number) {
    super(message)
    this.name = 'IdmsApiError'
    this.status = status
  }
}

http.interceptors.response.use(
  (resp) => resp,
  (err: AxiosError<ApiError>) => {
    const status = err.response?.status ?? 0
    const backendMsg = err.response?.data?.error
    const message =
      backendMsg ||
      (status === 0 ? '无法连接后端服务' : err.message || '请求失败')
    return Promise.reject(new IdmsApiError(message, status))
  },
)

// 登录态：本轮无真实认证，预留 token 注入位（将来后端做鉴权时启用）
export function setAuthToken(token: string | null) {
  if (token) {
    http.defaults.headers.common['Authorization'] = `Bearer ${token}`
  } else {
    delete http.defaults.headers.common['Authorization']
  }
}
