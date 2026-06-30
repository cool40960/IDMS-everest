import { Routes, Route, Navigate } from 'react-router-dom'
import { type ReactNode } from 'react'
import { useAuth } from './auth/authContext'
import LoginPage from './auth/LoginPage'
import Layout from './components/Layout'
import DatabaseListPage from './pages/DatabaseListPage'
import CreateDatabasePage from './pages/CreateDatabasePage'
import DatabaseDetailPage from './pages/DatabaseDetailPage'

// 路由守卫：未登录跳登录页
function RequireAuth({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <Layout>{children}</Layout>
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/databases"
        element={
          <RequireAuth>
            <DatabaseListPage />
          </RequireAuth>
        }
      />
      <Route
        path="/databases/new"
        element={
          <RequireAuth>
            <CreateDatabasePage />
          </RequireAuth>
        }
      />
      <Route
        path="/databases/:engineType/:name"
        element={
          <RequireAuth>
            <DatabaseDetailPage />
          </RequireAuth>
        }
      />
      <Route path="*" element={<Navigate to="/databases" replace />} />
    </Routes>
  )
}

export default App
