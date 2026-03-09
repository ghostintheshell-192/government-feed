import React, { useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { SlidersHorizontal } from 'lucide-react'
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
  const [showFilters, setShowFilters] = useState(false)
  const searchRef = useRef<HTMLDivElement>(null)
  const { t } = useTranslation()

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

  const hasAdvancedFilters =
    filters.date_from ||
    filters.date_to ||
    (filters.source_id && filters.source_id.length > 0)

  const applyRecentSearch = (query: string) => {
    onChange((prev) => ({ ...prev, search: query }))
    setShowRecent(false)
  }

  return (
    <div className="space-y-3">
      <div className="flex items-end gap-2">
        <div className="relative flex-1" ref={searchRef}>
          <Input
            type="text"
            placeholder={t('filterBar.searchPlaceholder')}
            value={filters.search || ''}
            onChange={(e) =>
              updateFilter('search', e.target.value || undefined)
            }
            onFocus={() => setShowRecent(true)}
            onBlur={() => {
              setTimeout(() => setShowRecent(false), 200)
            }}
          />
          {showRecent && recentSearches.length > 0 && !filters.search && (
            <div className="absolute z-10 mt-1 w-full rounded-md border bg-popover p-1 shadow-md">
              <p className="px-2 py-1 text-xs text-muted-foreground">
                {t('filterBar.recentSearches')}
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

        <Button
          variant={showFilters || hasAdvancedFilters ? 'default' : 'outline'}
          size="icon"
          onClick={() => setShowFilters(!showFilters)}
          title={t('filterBar.filtersToggle')}
        >
          <SlidersHorizontal className="h-4 w-4" />
        </Button>

        {hasFilters && (
          <>
            <Button variant="ghost" size="sm" onClick={clearFilters}>
              {t('filterBar.clearFilters')}
            </Button>
            <Button variant="outline" size="sm" onClick={onSaveSearch}>
              {t('filterBar.saveSearch')}
            </Button>
          </>
        )}
      </div>

      {showFilters && (
        <div className="flex flex-wrap items-end gap-3 rounded-md border bg-card p-3">
          <div className="min-w-[180px] flex-1">
            <label className="mb-1 block text-sm font-medium">{t('filterBar.sourceLabel')}</label>
            <select
              className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
              value={filters.source_id?.[0] ?? ''}
              onChange={(e) => {
                const val = e.target.value
                updateFilter('source_id', val ? [Number(val)] : undefined)
              }}
            >
              <option value="">{t('filterBar.allSources')}</option>
              {activeSources.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>

          <div className="min-w-[150px]">
            <label className="mb-1 block text-sm font-medium">{t('filterBar.dateFrom')}</label>
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

          <div className="min-w-[150px]">
            <label className="mb-1 block text-sm font-medium">{t('filterBar.dateTo')}</label>
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
        </div>
      )}
    </div>
  )
}
