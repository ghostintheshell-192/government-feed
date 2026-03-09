import { useCallback, useState } from 'react'

const STORAGE_KEY = 'government-feed:recent-searches'
const MAX_ITEMS = 8

function load(): string[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

function save(items: string[]): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(items))
}

export function useRecentSearches() {
  const [searches, setSearches] = useState<string[]>(load)

  const addSearch = useCallback((query: string) => {
    const trimmed = query.trim()
    if (!trimmed) return
    setSearches((prev) => {
      const filtered = prev.filter((s) => s !== trimmed)
      const next = [trimmed, ...filtered].slice(0, MAX_ITEMS)
      save(next)
      return next
    })
  }, [])

  const clearSearches = useCallback(() => {
    setSearches([])
    save([])
  }, [])

  return { searches, addSearch, clearSearches }
}
