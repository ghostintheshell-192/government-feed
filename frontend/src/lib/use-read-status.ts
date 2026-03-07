import { useCallback, useState } from 'react'

const STORAGE_KEY = 'government-feed:read-ids'

function loadReadIds(): Set<number> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return new Set()
    return new Set(JSON.parse(raw) as number[])
  } catch {
    return new Set()
  }
}

function saveReadIds(ids: Set<number>): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify([...ids]))
}

export function useReadStatus() {
  const [readIds, setReadIds] = useState<Set<number>>(loadReadIds)

  const isRead = useCallback((id: number) => readIds.has(id), [readIds])

  const markAsRead = useCallback((id: number) => {
    setReadIds((prev) => {
      const next = new Set(prev)
      next.add(id)
      saveReadIds(next)
      return next
    })
  }, [])

  return { isRead, markAsRead }
}
