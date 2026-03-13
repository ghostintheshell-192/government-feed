import { useEffect, useMemo, useRef, useState } from 'react'
import { useInfiniteQuery, useQuery, useQueryClient } from '@tanstack/react-query'
import { Download, X, Globe, Building2, Landmark, MapPin } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { ProgressBar } from '@/components/progress-bar'
import { FilterBar } from '@/components/filter-bar'
import { NewsCard } from '@/components/news-card'
import { fetchFeatures, fetchNews, fetchSources } from '@/lib/api'
import type { NewsFilters, Source } from '@/lib/types'
import { useDebounce } from '@/lib/use-debounce'
import { useReadStatus } from '@/lib/use-read-status'
import { useRecentSearches } from '@/lib/use-recent-searches'
import { useSavedSearches } from '@/lib/use-saved-searches'

const PAGE_SIZE = 20

const GEO_LEVELS = [
  { key: 'LOCAL', icon: MapPin, i18nKey: 'feed.geoLocal' },
  { key: 'NATIONAL', icon: Landmark, i18nKey: 'feed.geoNational' },
  { key: 'CONTINENTAL', icon: Building2, i18nKey: 'feed.geoContinental' },
  { key: 'GLOBAL', icon: Globe, i18nKey: 'feed.geoGlobal' },
] as const

type GeoLevel = (typeof GEO_LEVELS)[number]['key']

export default function Feed() {
  const [filters, setFilters] = useState<NewsFilters>({})
  const debouncedFilters = useDebounce(filters, 300)
  const { isRead, markAsRead } = useReadStatus()
  const queryClient = useQueryClient()
  const { searches: recentSearches, addSearch } = useRecentSearches()
  const { savedSearches, saveSearch, removeSearch } = useSavedSearches()
  const { t } = useTranslation()

  // Geographic filter state — null means "all" (no filtering)
  const [activeGeoLevels, setActiveGeoLevels] = useState<Set<GeoLevel> | null>(null)

  // Import-all state
  const [importingAll, setImportingAll] = useState(false)
  const [importAllProgress, setImportAllProgress] = useState<{
    current: number; total: number; source: string
  } | null>(null)
  const [importAllResult, setImportAllResult] = useState<{
    imported: number; errors: number; total: number
  } | null>(null)

  // Track debounced search to add to recent searches
  const prevSearchRef = useRef<string | undefined>()
  useEffect(() => {
    const current = debouncedFilters.search
    if (current && current !== prevSearchRef.current) {
      addSearch(current)
    }
    prevSearchRef.current = current
  }, [debouncedFilters.search, addSearch])

  const { data: features } = useQuery({
    queryKey: ['features'],
    queryFn: fetchFeatures,
  })

  const { data: sources = [] } = useQuery({
    queryKey: ['sources'],
    queryFn: fetchSources,
  })

  const sourceMap = new Map(sources.map((s) => [s.id, s.name]))

  // Build geo level → source_ids mapping
  const geoSourceIds = useMemo(() => {
    const map: Record<string, number[]> = { LOCAL: [], NATIONAL: [], CONTINENTAL: [], GLOBAL: [] }
    for (const s of sources) {
      if (s.geographic_level && s.geographic_level in map) {
        map[s.geographic_level].push(s.id)
      }
    }
    return map
  }, [sources])

  // Compute effective source_id filter based on geo selection
  const geoFilteredSourceIds = useMemo(() => {
    if (!activeGeoLevels) return undefined
    const ids: number[] = []
    for (const level of activeGeoLevels) {
      ids.push(...(geoSourceIds[level] ?? []))
    }
    return ids.length > 0 ? ids : [-1] // -1 = no results (empty filter)
  }, [activeGeoLevels, geoSourceIds])

  // Merge geo filter into the user's filters for the API query
  const effectiveFilters = useMemo<NewsFilters>(() => {
    if (!geoFilteredSourceIds) return debouncedFilters
    // Geo filter overrides source_id (they're the same concept)
    return { ...debouncedFilters, source_id: geoFilteredSourceIds }
  }, [debouncedFilters, geoFilteredSourceIds])

  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
  } = useInfiniteQuery({
    queryKey: ['news', effectiveFilters],
    queryFn: ({ pageParam = 0 }) =>
      fetchNews(PAGE_SIZE, pageParam as number, effectiveFilters),
    initialPageParam: 0,
    getNextPageParam: (lastPage) =>
      lastPage.pagination.has_more
        ? lastPage.pagination.offset + lastPage.pagination.limit
        : undefined,
  })

  const allItems = data?.pages.flatMap((p) => p.items) ?? []
  const total = data?.pages[0]?.pagination.total ?? 0


  const toggleGeoLevel = (level: GeoLevel) => {
    setActiveGeoLevels((prev) => {
      if (prev === null) {
        // First click: select only this level
        return new Set([level])
      }
      const next = new Set(prev)
      if (next.has(level)) {
        next.delete(level)
        // If nothing selected, go back to "all"
        return next.size === 0 ? null : next
      }
      next.add(level)
      // If all 4 selected, go back to "all"
      return next.size === 4 ? null : next
    })
  }

  const updateNewsItem = (id: number, updates: Record<string, string>) => {
    queryClient.setQueryData(
      ['news', effectiveFilters],
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (old: any) => {
        if (!old) return old
        return {
          ...old,
          pages: old.pages.map((page: (typeof data)['pages'][number]) => ({
            ...page,
            items: page.items.map((item) =>
              item.id === id ? { ...item, ...updates } : item,
            ),
          })),
        }
      },
    )
  }

  const handleSummaryUpdate = (id: number, summary: string) => {
    updateNewsItem(id, { summary })
  }

  const handleSaveSearch = () => {
    const name = prompt(t('feed.saveSearchPrompt'))
    if (name) {
      saveSearch(name, filters)
    }
  }

  const importAll = async () => {
    setImportingAll(true)
    setImportAllProgress(null)
    setImportAllResult(null)
    try {
      const res = await fetch('/api/sources/import-all', { method: 'POST' })
      if (!res.ok || !res.body) throw new Error(`Errore ${res.status}`)

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''
        for (const line of lines) {
          if (!line.trim()) continue
          const data = JSON.parse(line)
          if (data.done) {
            setImportAllResult({ imported: data.imported, errors: data.errors, total: data.total })
          } else {
            setImportAllProgress({ current: data.current, total: data.total, source: data.source })
          }
        }
      }

      queryClient.invalidateQueries({ queryKey: ['news'], refetchType: 'all' })
      queryClient.invalidateQueries({ queryKey: ['sources'] })
    } catch {
      alert(t('feed.errorImportAll'))
    } finally {
      setImportingAll(false)
      setImportAllProgress(null)
    }
  }

  const applySavedSearch = (searchFilters: NewsFilters) => {
    setFilters(searchFilters)
  }

  const describeSavedFilters = (f: NewsFilters): string => {
    const parts: string[] = []
    if (f.search) parts.push(`"${f.search}"`)
    if (f.source_id?.length) {
      const names = f.source_id
        .map((id) => sourceMap.get(id))
        .filter(Boolean)
      if (names.length) parts.push(names.join(', '))
    }
    if (f.date_from || f.date_to) parts.push(t('feed.dateRange'))
    return parts.length ? parts.join(' + ') : t('feed.allFilters')
  }

  return (
    <div className="flex gap-6 px-4 py-6 md:px-6">
      {/* Geographic sidebar */}
      <aside className="hidden w-40 shrink-0 md:block">
        <nav className="sticky top-24 space-y-2">
          {/* "All" button */}
          <button
            type="button"
            onClick={() => setActiveGeoLevels(null)}
            className={`flex w-full items-center gap-2 rounded-lg px-3 py-2.5 text-left text-sm font-medium transition-colors ${
              activeGeoLevels === null
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:bg-muted hover:text-foreground'
            }`}
          >
            {t('feed.geoAll')}
          </button>

          {GEO_LEVELS.map(({ key, icon: Icon, i18nKey }) => (
              <button
                key={key}
                type="button"
                onClick={() => toggleGeoLevel(key)}
                className={`flex w-full items-center gap-2 rounded-lg px-3 py-2.5 text-left text-sm font-medium transition-colors ${
                  activeGeoLevels !== null && activeGeoLevels.has(key)
                    ? 'bg-primary text-primary-foreground'
                    : activeGeoLevels === null
                      ? 'text-foreground hover:bg-muted'
                      : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                }`}
              >
                <Icon className="h-4 w-4 shrink-0" />
                <span className="flex-1">{t(i18nKey)}</span>
              </button>
          ))}
        </nav>
      </aside>

      {/* Mobile geo bar */}
      <div className="mb-4 flex gap-1.5 overflow-x-auto md:hidden">
        <Button
          size="sm"
          variant={activeGeoLevels === null ? 'default' : 'outline'}
          onClick={() => setActiveGeoLevels(null)}
        >
          {t('feed.geoAll')}
        </Button>
        {GEO_LEVELS.map(({ key, icon: Icon, i18nKey }) => (
          <Button
            key={key}
            size="sm"
            variant={activeGeoLevels?.has(key) ? 'default' : 'outline'}
            onClick={() => toggleGeoLevel(key)}
            className="shrink-0"
          >
            <Icon className="mr-1 h-3.5 w-3.5" />
            {t(i18nKey)}
          </Button>
        ))}
      </div>

      {/* Main content */}
      <div className="min-w-0 flex-1 pr-4 md:pr-8">
        <div className="mb-4">
          <FilterBar
            filters={filters}
            sources={sources}
            recentSearches={recentSearches}
            onChange={setFilters}
            onSaveSearch={handleSaveSearch}
          />
        </div>

        {/* Import-all */}
        <div className="mb-4 flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={importAll}
            disabled={importingAll || sources.length === 0}
          >
            <Download className="mr-1.5 h-4 w-4" />
            {importingAll
              ? importAllProgress
                ? `${importAllProgress.current}/${importAllProgress.total}`
                : t('feed.importAll')
              : t('feed.importAll')}
          </Button>
          {importAllResult && (
            <div className="flex flex-1 items-center justify-between rounded-lg border bg-muted/50 px-3 py-2 text-xs">
              <span>
                {t('feed.importAllResult', {
                  total: importAllResult.total,
                  imported: importAllResult.imported,
                  errors: importAllResult.errors,
                })}
              </span>
              <Button
                variant="outline"
                size="icon"
                className="ml-2 h-5 w-5 shrink-0 border-primary text-primary hover:bg-primary hover:text-primary-foreground"
                onClick={() => setImportAllResult(null)}
              >
                &times;
              </Button>
            </div>
          )}
        </div>

        {importingAll && importAllProgress && (
          <div className="mb-4 rounded-lg border bg-muted/50 px-4 py-3">
            <ProgressBar
              current={importAllProgress.current}
              total={importAllProgress.total}
              label={t('feed.importingSource', {
                current: importAllProgress.current,
                total: importAllProgress.total,
                source: importAllProgress.source,
              })}
            />
          </div>
        )}

        {savedSearches.length > 0 && (
          <div className="mb-6 flex flex-wrap items-center gap-2">
            <span className="text-xs text-muted-foreground">{t('feed.savedSearches')}</span>
            {savedSearches.map((saved) => (
              <Badge
                key={saved.id}
                variant="secondary"
                className="cursor-pointer gap-1 pr-1"
                title={describeSavedFilters(saved.filters)}
                onClick={() => applySavedSearch(saved.filters)}
              >
                {saved.name}
                <button
                  type="button"
                  className="ml-0.5 rounded-full p-0.5 hover:bg-muted-foreground/20"
                  onClick={(e) => {
                    e.stopPropagation()
                    removeSearch(saved.id)
                  }}
                  aria-label={t('feed.removeSearch', { name: saved.name })}
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            ))}
          </div>
        )}

        {isLoading ? (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="rounded-lg border p-6">
                <Skeleton className="mb-3 h-5 w-3/4" />
                <Skeleton className="mb-2 h-4 w-1/4" />
                <Skeleton className="h-4 w-full" />
              </div>
            ))}
          </div>
        ) : allItems.length === 0 ? (
          <div className="py-16 text-center">
            <h3 className="text-xl font-semibold text-muted-foreground">
              {t('feed.noNewsFound')}
            </h3>
            <p className="mt-2 text-muted-foreground">
              {total === 0 && !Object.keys(debouncedFilters).length ? (
                <>
                  {t('feed.goToSources')}{' '}
                  <a href="/sources" className="text-primary underline">
                    {t('feed.sourcesLink')}
                  </a>{' '}
                  {t('feed.noNewsHelpAdd')}
                </>
              ) : (
                t('feed.noNewsHelpFilter')
              )}
            </p>
          </div>
        ) : (
          <>
            <p className="mb-4 text-sm text-muted-foreground">
              {t('feed.newsCount', { count: total })}
            </p>

            <div className="space-y-4">
              {allItems.map((item) => (
                <NewsCard
                  key={item.id}
                  item={item}
                  sourceName={sourceMap.get(item.source_id)}
                  isRead={isRead(item.id)}
                  aiEnabled={features?.ai_enabled ?? false}
                  searchTerm={debouncedFilters.search}
                  onRead={markAsRead}
                  onSummaryUpdate={handleSummaryUpdate}
                />
              ))}
            </div>

            {hasNextPage && (
              <div className="mt-6 text-center">
                <Button
                  variant="outline"
                  onClick={() => fetchNextPage()}
                  disabled={isFetchingNextPage}
                >
                  {isFetchingNextPage
                    ? t('common.loading')
                    : t('feed.loadMore')}
                </Button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
