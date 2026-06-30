import { describe, it, expect } from 'vitest'
import { IdmsApiError } from '../api/client'

describe('IdmsApiError', () => {
  it('携带 message 和 status', () => {
    const e = new IdmsApiError('实例已存在', 409)
    expect(e.message).toBe('实例已存在')
    expect(e.status).toBe(409)
    expect(e.name).toBe('IdmsApiError')
    expect(e).toBeInstanceOf(Error)
  })
})
