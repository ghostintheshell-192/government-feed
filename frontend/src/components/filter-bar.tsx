import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import type { NewsFilters, Source } from '@/lib/types'

interface FilterBarProps {
  filters: NewsFilters
  sources: Source[]
  onChange: (filters: NewsFilters) => void
}

export function FilterBar({ filters, sources, onChange }: FilterBarProps) {
  const activeSources = sources.filter((s) => s.is_active)

  const updateFilter = <K extends keyof NewsFilters>(
    key: K,
    value: NewsFilters[K],
  ) => {
    onChange({ ...filters, [key]: value })
  }

  const clearFilters = () => {
    onChange({})
  }

  const hasFilters =
    filters.search ||
    filters.date_from ||
    filters.date_to ||
    (filters.source_id && filters.source_id.length > 0)

  return (
    <div className="flex flex-wrap items-end gap-3">
      <div className="min-w-[200px] flex-1">
        <label className="mb-1 block text-sm font-medium">Cerca</label>
        <Input
          type="text"
          placeholder="Cerca nelle notizie..."
          value={filters.search || ''}
          onChange={(e) => updateFilter('search', e.target.value || undefined)}
        />
      </div>

      <div className="min-w-[180px]">
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

      <div className="min-w-[150px]">
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

      <div className="min-w-[150px]">
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
        <Button variant="ghost" size="sm" onClick={clearFilters}>
          Pulisci filtri
        </Button>
      )}
    </div>
  )
}
