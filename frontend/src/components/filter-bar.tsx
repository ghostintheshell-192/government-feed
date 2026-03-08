import React, { useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import type { NewsFilters, Source } from '@/lib/types'

interface FilterBarProps {
  filters: NewsFilters
  sources: Source[]
  recentSearches: string[]
  onChange: React.Dispatch<React.SetStateAction<NewsFilters>>
  onSaveSearch: () => void
}

export function FilterBar({
  filters,
  sources,
  recentSearches,
  onChange,
  onSaveSearch,
}: FilterBarProps) {
  const activeSources = sources.filter((s) => s.is_active)
  const [showRecent, setShowRecent] = useState(false)
  const searchRef = useRef<HTMLDivElement>(null)

  const updateFilter = <K extends keyof NewsFilters>(
    key: K,
    value: NewsFilters[K],
  ) => {
    onChange((prev) => ({ ...prev, [key]: value }))
  }

  const clearFilters = () => {
    onChange({})
  }

  const hasFilters =
    filters.search ||
    filters.date_from ||
    filters.date_to ||
    (filters.source_id && filters.source_id.length > 0)

  const applyRecentSearch = (query: string) => {
    onChange((prev) => ({ ...prev, search: query }))
    setShowRecent(false)
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-end gap-3">
        <div className="relative w-full flex-1 sm:min-w-[200px]" ref={searchRef}>
          <label className="mb-1 block text-sm font-medium">Cerca</label>
          <Input
            type="text"
            placeholder="Cerca nelle notizie..."
            value={filters.search || ''}
            onChange={(e) =>
              updateFilter('search', e.target.value || undefined)
            }
            onFocus={() => setShowRecent(true)}
            onBlur={() => {
              // Delay to allow click on dropdown items
              setTimeout(() => setShowRecent(false), 200)
            }}
          />
          {showRecent && recentSearches.length > 0 && !filters.search && (
            <div className="absolute z-10 mt-1 w-full rounded-md border bg-popover p-1 shadow-md">
              <p className="px-2 py-1 text-xs text-muted-foreground">
                Ricerche recenti
              </p>
              {recentSearches.map((query) => (
                <button
                  key={query}
                  type="button"
                  className="w-full rounded-sm px-2 py-1.5 text-left text-sm hover:bg-accent"
                  onMouseDown={(e) => {
                    e.preventDefault()
                    applyRecentSearch(query)
                  }}
                >
                  {query}
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="w-full sm:w-auto sm:min-w-[180px]">
          <label className="mb-1 block text-sm font-medium">Fonte</label>
          <select
            className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
            value={filters.source_id?.[0] ?? ''}
            onChange={(e) => {
              const val = e.target.value
              updateFilter('source_id', val ? [Number(val)] : undefined)
            }}
          >
            <option value="">Tutte le fonti</option>
            {activeSources.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
        </div>

        <div className="min-w-0 flex-1 sm:min-w-[150px] sm:flex-none">
          <label className="mb-1 block text-sm font-medium">Da</label>
          <Input
            type="date"
            value={filters.date_from?.split('T')[0] || ''}
            onChange={(e) =>
              updateFilter(
                'date_from',
                e.target.value ? e.target.value + 'T00:00:00' : undefined,
              )
            }
          />
        </div>

        <div className="min-w-0 flex-1 sm:min-w-[150px] sm:flex-none">
          <label className="mb-1 block text-sm font-medium">A</label>
          <Input
            type="date"
            value={filters.date_to?.split('T')[0] || ''}
            onChange={(e) =>
              updateFilter(
                'date_to',
                e.target.value ? e.target.value + 'T23:59:59' : undefined,
              )
            }
          />
        </div>

        {hasFilters && (
          <>
            <Button variant="ghost" size="sm" onClick={clearFilters}>
              Pulisci filtri
            </Button>
            <Button variant="outline" size="sm" onClick={onSaveSearch}>
              Salva ricerca
            </Button>
          </>
        )}
      </div>
    </div>
  )
}
