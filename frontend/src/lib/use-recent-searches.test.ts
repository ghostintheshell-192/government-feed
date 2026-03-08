import { act, renderHook } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import { useRecentSearches } from './use-recent-searches'

describe('useRecentSearches', () => {
  afterEach(() => {
    localStorage.clear()
  })

  it('starts empty', () => {
    const { result } = renderHook(() => useRecentSearches())
    expect(result.current.searches).toEqual([])
  })

  it('adds a search', () => {
    const { result } = renderHook(() => useRecentSearches())

    act(() => {
      result.current.addSearch('interest rates')
    })

    expect(result.current.searches).toEqual(['interest rates'])
  })

  it('most recent search is first', () => {
    const { result } = renderHook(() => useRecentSearches())

    act(() => {
      result.current.addSearch('first')
      result.current.addSearch('second')
    })

    expect(result.current.searches[0]).toBe('second')
  })

  it('deduplicates searches', () => {
    const { result } = renderHook(() => useRecentSearches())

    act(() => {
      result.current.addSearch('test')
      result.current.addSearch('other')
      result.current.addSearch('test')
    })

    expect(result.current.searches).toEqual(['test', 'other'])
  })

  it('limits to 8 items', () => {
    const { result } = renderHook(() => useRecentSearches())

    act(() => {
      for (let i = 0; i < 12; i++) {
        result.current.addSearch(`search ${i}`)
      }
    })

    expect(result.current.searches.length).toBe(8)
    expect(result.current.searches[0]).toBe('search 11') // Most recent
  })

  it('ignores empty searches', () => {
    const { result } = renderHook(() => useRecentSearches())

    act(() => {
      result.current.addSearch('')
      result.current.addSearch('   ')
    })

    expect(result.current.searches).toEqual([])
  })

  it('clears all searches', () => {
    const { result } = renderHook(() => useRecentSearches())

    act(() => {
      result.current.addSearch('test')
      result.current.clearSearches()
    })

    expect(result.current.searches).toEqual([])
    expect(localStorage.getItem('government-feed:recent-searches')).toBe('[]')
  })

  it('persists to localStorage', () => {
    const { result } = renderHook(() => useRecentSearches())

    act(() => {
      result.current.addSearch('persisted')
    })

    const stored = JSON.parse(localStorage.getItem('government-feed:recent-searches')!)
    expect(stored).toEqual(['persisted'])
  })
})
