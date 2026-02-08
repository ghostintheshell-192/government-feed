import { useEffect, useRef, useState } from 'react'
import { useInfiniteQuery, useQuery, useQueryClient } from '@tanstack/react-query'
import { X } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { FilterBar } from '@/components/filter-bar'
import { NewsCard } from '@/components/news-card'
import { fetchFeatures, fetchNews, fetchSources } from '@/lib/api'
import type { NewsFilters } from '@/lib/types'
import { useDebounce } from '@/lib/use-debounce'
import { useReadStatus } from '@/lib/use-read-status'
import { useRecentSearches } from '@/lib/use-recent-searches'
import { useSavedSearches } from '@/lib/use-saved-searches'

const PAGE_SIZE = 20

export default function Feed() {
  const [filters, setFilters] = useState<NewsFilters>({})
  const debouncedFilters = useDebounce(filters, 300)
  const { isRead, markAsRead } = useReadStatus()
  const queryClient = useQueryClient()
  const { searches: recentSearches, addSearch } = useRecentSearches()
  const { savedSearches, saveSearch, removeSearch } = useSavedSearches()

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

  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
  } = useInfiniteQuery({
    queryKey: ['news', debouncedFilters],
    queryFn: ({ pageParam = 0 }) =>
      fetchNews(PAGE_SIZE, pageParam as number, debouncedFilters),
    initialPageParam: 0,
    getNextPageParam: (lastPage) =>
      lastPage.pagination.has_more
        ? lastPage.pagination.offset + lastPage.pagination.limit
        : undefined,
  })

  const allItems = data?.pages.flatMap((p) => p.items) ?? []
  const total = data?.pages[0]?.pagination.total ?? 0

  const sourceMap = new Map(sources.map((s) => [s.id, s.name]))

  const updateNewsItem = (id: number, updates: Record<string, string>) => {
    queryClient.setQueryData(
      ['news', debouncedFilters],
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

  const handleContentUpdate = (id: number, content: string) => {
    updateNewsItem(id, { content })
  }

  const handleSaveSearch = () => {
    const name = prompt('Nome per questa ricerca:')
    if (name) {
      saveSearch(name, filters)
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
    if (f.date_from || f.date_to) parts.push('date range')
    return parts.length ? parts.join(' + ') : 'tutti i filtri'
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-6 md:px-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="mt-1 text-muted-foreground">
          Le ultime notizie dai feed istituzionali
        </p>
      </div>

      <div className="mb-4">
        <FilterBar
          filters={filters}
          sources={sources}
          recentSearches={recentSearches}
          onChange={setFilters}
          onSaveSearch={handleSaveSearch}
        />
      </div>

      {savedSearches.length > 0 && (
        <div className="mb-6 flex flex-wrap items-center gap-2">
          <span className="text-xs text-muted-foreground">Salvate:</span>
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
                aria-label={`Rimuovi ${saved.name}`}
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
            Nessuna notizia trovata
          </h3>
          <p className="mt-2 text-muted-foreground">
            {total === 0 && !Object.keys(debouncedFilters).length ? (
              <>
                Vai su{' '}
                <a href="/sources" className="text-primary underline">
                  Gestione Sources
                </a>{' '}
                per aggiungere feed e importare le notizie.
              </>
            ) : (
              'Prova a modificare i filtri di ricerca.'
            )}
          </p>
        </div>
      ) : (
        <>
          <p className="mb-4 text-sm text-muted-foreground">
            {total} notizie trovate
          </p>

          <div className="space-y-4">
            {allItems.map((item) => (
              <NewsCard
                key={item.id}
                item={item}
                sourceName={sourceMap.get(item.source_id)}
                isRead={isRead(item.id)}
                aiEnabled={features?.ai_enabled ?? false}
                onRead={markAsRead}
                onSummaryUpdate={handleSummaryUpdate}
                onContentUpdate={handleContentUpdate}
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
                  ? 'Caricamento...'
                  : 'Carica altre notizie'}
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
