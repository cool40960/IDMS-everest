import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen, act } from '@testing-library/react'
import { AuthProvider, useAuth } from '../auth/authContext'

function Probe() {
  const { isAuthenticated, username, login, logout } = useAuth()
  return (
    <div>
      <span data-testid="state">{isAuthenticated ? `in:${username}` : 'out'}</span>
      <button onClick={() => login('alice')}>login</button>
      <button onClick={logout}>logout</button>
    </div>
  )
}

beforeEach(() => localStorage.clear())

describe('authContext', () => {
  it('初始未登录', () => {
    render(<AuthProvider><Probe /></AuthProvider>)
    expect(screen.getByTestId('state').textContent).toBe('out')
  })

  it('登录后置位并持久化', () => {
    render(<AuthProvider><Probe /></AuthProvider>)
    act(() => screen.getByText('login').click())
    expect(screen.getByTestId('state').textContent).toBe('in:alice')
    expect(localStorage.getItem('idms_auth_user')).toBe('alice')
  })

  it('退出后清除', () => {
    render(<AuthProvider><Probe /></AuthProvider>)
    act(() => screen.getByText('login').click())
    act(() => screen.getByText('logout').click())
    expect(screen.getByTestId('state').textContent).toBe('out')
    expect(localStorage.getItem('idms_auth_user')).toBeNull()
  })
})
