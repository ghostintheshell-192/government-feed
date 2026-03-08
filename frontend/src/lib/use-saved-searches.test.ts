import { act, renderHook } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { useSavedSearches } from './use-saved-searches'

describe('useSavedSearches', () => {
  afterEach(() => {
    localStorage.clear()
  })

  it('starts empty', () => {
    const { result } = renderHook(() => useSavedSearches())
    expect(result.current.savedSearches).toEqual([])
  })

  it('saves a search with filters', () => {
    const { result } = renderHook(() => useSavedSearches())

    act(() => {
      result.current.saveSearch('My Search', {
        search: 'interest',
        source_id: [1, 2],
      })
    })

    expect(result.current.savedSearches.length).toBe(1)
    expect(result.current.savedSearches[0].name).toBe('My Search')
    expect(result.current.savedSearches[0].filters.search).toBe('interest')
  })

  it('generates unique ids', () => {
    vi.useFakeTimers()
    const { result } = renderHook(() => useSavedSearches())

    act(() => {
      result.current.saveSearch('First', { search: 'a' })
    })
    vi.advanceTimersByTime(1)
    act(() => {
      result.current.saveSearch('Second', { search: 'b' })
    })

    const ids = result.current.savedSearches.map((s) => s.id)
    expect(new Set(ids).size).toBe(2) // All unique
    vi.useRealTimers()
  })

  it('removes a search by id', () => {
    vi.useFakeTimers()
    const { result } = renderHook(() => useSavedSearches())

    act(() => {
      result.current.saveSearch('Keep', { search: 'keep' })
    })
    vi.advanceTimersByTime(1)
    act(() => {
      result.current.saveSearch('Remove', { search: 'remove' })
    })

    const idToRemove = result.current.savedSearches.find(
      (s) => s.name === 'Remove',
    )!.id

    act(() => {
      result.current.removeSearch(idToRemove)
    })

    expect(result.current.savedSearches.length).toBe(1)
    expect(result.current.savedSearches[0].name).toBe('Keep')
    vi.useRealTimers()
  })

  it('ignores empty names', () => {
    const { result } = renderHook(() => useSavedSearches())

    act(() => {
      result.current.saveSearch('', { search: 'test' })
      result.current.saveSearch('   ', { search: 'test' })
    })

    expect(result.current.savedSearches).toEqual([])
  })

  it('persists to localStorage', () => {
    const { result } = renderHook(() => useSavedSearches())

    act(() => {
      result.current.saveSearch('Saved', { search: 'test' })
    })

    const stored = JSON.parse(
      localStorage.getItem('government-feed:saved-searches')!,
    )
    expect(stored.length).toBe(1)
    expect(stored[0].name).toBe('Saved')
  })

  it('loads from localStorage on init', () => {
    localStorage.setItem(
      'government-feed:saved-searches',
      JSON.stringify([
        { id: '1', name: 'Existing', filters: { search: 'old' } },
      ]),
    )

    const { result } = renderHook(() => useSavedSearches())
    expect(result.current.savedSearches.length).toBe(1)
    expect(result.current.savedSearches[0].name).toBe('Existing')
  })
})
