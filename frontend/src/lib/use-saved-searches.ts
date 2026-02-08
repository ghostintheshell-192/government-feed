import { useCallback, useState } from 'react'
import type { NewsFilters } from './types'

const STORAGE_KEY = 'government-feed:saved-searches'

export interface SavedSearch {
  id: string
  name: string
  filters: NewsFilters
}

function load(): SavedSearch[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

function save(items: SavedSearch[]): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(items))
}

export function useSavedSearches() {
  const [savedSearches, setSavedSearches] = useState<SavedSearch[]>(load)

  const saveSearch = useCallback((name: string, filters: NewsFilters) => {
    const trimmed = name.trim()
    if (!trimmed) return
    setSavedSearches((prev) => {
      const next = [
        ...prev,
        { id: Date.now().toString(), name: trimmed, filters },
      ]
      save(next)
      return next
    })
  }, [])

  const removeSearch = useCallback((id: string) => {
    setSavedSearches((prev) => {
      const next = prev.filter((s) => s.id !== id)
      save(next)
      return next
    })
  }, [])

  return { savedSearches, saveSearch, removeSearch }
}
