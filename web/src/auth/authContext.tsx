import { createContext, useContext, useState, type ReactNode } from 'react'

// 登录态。本轮无真实认证：登录即在本地存个标记，路由守卫据此放行。
// 将来后端做鉴权时，这里改为存真实 token + 调登录接口。

interface AuthState {
  isAuthenticated: boolean
  username: string | null
  login: (username: string) => void
  logout: () => void
}

const AuthContext = createContext<AuthState | undefined>(undefined)

const STORAGE_KEY = 'idms_auth_user'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [username, setUsername] = useState<string | null>(
    () => localStorage.getItem(STORAGE_KEY),
  )

  const login = (name: string) => {
    localStorage.setItem(STORAGE_KEY, name)
    setUsername(name)
  }
  const logout = () => {
    localStorage.removeItem(STORAGE_KEY)
    setUsername(null)
  }

  return (
    <AuthContext.Provider
      value={{ isAuthenticated: !!username, username, login, logout }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth 必须在 AuthProvider 内使用')
  return ctx
}
