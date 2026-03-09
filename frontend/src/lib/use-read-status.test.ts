import { act, renderHook } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import { useReadStatus } from './use-read-status'

describe('useReadStatus', () => {
  afterEach(() => {
    localStorage.clear()
  })

  it('starts with no read items', () => {
    const { result } = renderHook(() => useReadStatus())
    expect(result.current.isRead(1)).toBe(false)
    expect(result.current.isRead(2)).toBe(false)
  })

  it('marks item as read', () => {
    const { result } = renderHook(() => useReadStatus())

    act(() => {
      result.current.markAsRead(42)
    })

    expect(result.current.isRead(42)).toBe(true)
    expect(result.current.isRead(1)).toBe(false)
  })

  it('persists to localStorage', () => {
    const { result } = renderHook(() => useReadStatus())

    act(() => {
      result.current.markAsRead(1)
      result.current.markAsRead(2)
    })

    const stored = JSON.parse(localStorage.getItem('government-feed:read-ids')!)
    expect(stored).toContain(1)
    expect(stored).toContain(2)
  })

  it('loads from localStorage on init', () => {
    localStorage.setItem('government-feed:read-ids', JSON.stringify([10, 20]))

    const { result } = renderHook(() => useReadStatus())
    expect(result.current.isRead(10)).toBe(true)
    expect(result.current.isRead(20)).toBe(true)
    expect(result.current.isRead(30)).toBe(false)
  })

  it('handles corrupted localStorage gracefully', () => {
    localStorage.setItem('government-feed:read-ids', 'not json')

    const { result } = renderHook(() => useReadStatus())
    expect(result.current.isRead(1)).toBe(false) // Falls back to empty
  })
})
