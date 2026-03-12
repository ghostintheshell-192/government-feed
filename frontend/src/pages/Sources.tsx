import { useEffect, useState, useMemo } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import { Search, Check, Plus } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'
import {
  discoverFeeds,
  fetchCatalog,
  subscribeToCatalog,
  unsubscribeFromCatalog,
  type DiscoveredFeed,
} from '@/lib/api'
import type { CatalogSource } from '@/lib/types'

interface Source {
  id: number
  name: string
  description?: string
  feed_url: string
  source_type: string
  category?: string
  update_frequency_minutes: number
  is_active: boolean
  last_fetched?: string
}

interface SourceFormData {
  name: string
  description: string
  feed_url: string
  source_type: string
  category: string
  update_frequency_minutes: number
  is_active: boolean
}

const emptyForm: SourceFormData = {
  name: '',
  description: '',
  feed_url: '',
  source_type: 'RSS',
  category: '',
  update_frequency_minutes: 60,
  is_active: true,
}

function useDebounce<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value)
  useMemo(() => {
    const timer = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])
  return debounced
}

export default function Sources() {
  const queryClient = useQueryClient()
  const { t } = useTranslation()

  // Subscribed sources state
  const [sources, setSources] = useState<Source[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Catalog search state
  const [searchQuery, setSearchQuery] = useState('')
  const debouncedSearch = useDebounce(searchQuery, 300)
  const [catalogResults, setCatalogResults] = useState<CatalogSource[]>([])
  const [catalogTotal, setCatalogTotal] = useState(0)
  const [catalogLoading, setCatalogLoading] = useState(false)
  const [catalogOffset, setCatalogOffset] = useState(0)
  const [catalogHasMore, setCatalogHasMore] = useState(false)
  const isSearching = searchQuery.trim().length > 0

  // Modal state
  const [showModal, setShowModal] = useState(false)
  const [editMode, setEditMode] = useState(false)
  const [editId, setEditId] = useState<number | null>(null)
  const [formData, setFormData] = useState<SourceFormData>({ ...emptyForm })

  // Feed discovery state (inside modal)
  const [discoveryQuery, setDiscoveryQuery] = useState('')
  const [discovering, setDiscovering] = useState(false)
  const [discoveredFeeds, setDiscoveredFeeds] = useState<DiscoveredFeed[]>([])
  const [searchedSites, setSearchedSites] = useState<string[]>([])
  const [discoveryDone, setDiscoveryDone] = useState(false)
  const [addingFeed, setAddingFeed] = useState<string | null>(null)

  // Action state
  const [processing, setProcessing] = useState<number | null>(null)
  const [subscribing, setSubscribing] = useState<number | null>(null)

  useEffect(() => {
    loadSources()
  }, [])

  // Catalog search effect
  useEffect(() => {
    if (debouncedSearch.trim()) {
      searchCatalog(debouncedSearch.trim(), 0)
    } else {
      setCatalogResults([])
      setCatalogTotal(0)
      setCatalogOffset(0)
      setCatalogHasMore(false)
    }
  }, [debouncedSearch])

  const loadSources = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('/api/sources')
      if (!res.ok) throw new Error(`Errore ${res.status}`)
      const data = await res.json()
      setSources(data)
    } catch {
      setError(t('sources.errorLoad'))
    } finally {
      setLoading(false)
    }
  }

  const searchCatalog = async (query: string, offset: number) => {
    setCatalogLoading(true)
    try {
      const result = await fetchCatalog(20, offset, { search: query })
      if (offset === 0) {
        setCatalogResults(result.items)
      } else {
        setCatalogResults((prev) => [...prev, ...result.items])
      }
      setCatalogTotal(result.pagination.total)
      setCatalogOffset(offset + result.pagination.limit)
      setCatalogHasMore(result.pagination.has_more)
    } catch {
      // silently fail
    } finally {
      setCatalogLoading(false)
    }
  }

  const handleSubscribe = async (sourceId: number) => {
    setSubscribing(sourceId)
    try {
      await subscribeToCatalog(sourceId)
      await loadSources()
      queryClient.invalidateQueries({ queryKey: ['news'] })
      // Update catalog results to reflect subscription
      setCatalogResults((prev) =>
        prev.map((s) => (s.id === sourceId ? { ...s, is_subscribed: true } : s))
      )
    } catch {
      alert(t('sources.errorSubscribe'))
    } finally {
      setSubscribing(null)
    }
  }

  const handleUnsubscribe = async (id: number) => {
    if (!confirm(t('sources.confirmUnsubscribe'))) return
    try {
      const res = await fetch(`/api/sources/${id}`, { method: 'DELETE' })
      if (!res.ok) throw new Error(`Errore ${res.status}`)
      await loadSources()
      queryClient.invalidateQueries({ queryKey: ['news'] })
      // Update catalog results if searching
      setCatalogResults((prev) =>
        prev.map((s) => (s.id === id ? { ...s, is_subscribed: false } : s))
      )
    } catch {
      alert(t('sources.errorUnsubscribe'))
    }
  }

  const openAddModal = () => {
    setEditMode(false)
    setEditId(null)
    setFormData({ ...emptyForm })
    setDiscoveryQuery('')
    setDiscoveredFeeds([])
    setSearchedSites([])
    setDiscoveryDone(false)
    setShowModal(true)
  }

  const openEditModal = (source: Source) => {
    setEditMode(true)
    setEditId(source.id)
    setFormData({
      name: source.name,
      description: source.description || '',
      feed_url: source.feed_url,
      source_type: source.source_type,
      category: source.category || '',
      update_frequency_minutes: source.update_frequency_minutes,
      is_active: source.is_active,
    })
    setShowModal(true)
  }

  const closeModal = () => {
    setShowModal(false)
    setFormData({ ...emptyForm })
  }

  const saveSource = async () => {
    if (!formData.name || !formData.feed_url) {
      alert(t('sources.errorValidation'))
      return
    }

    const url = editMode ? `/api/sources/${editId}` : '/api/sources'
    const method = editMode ? 'PUT' : 'POST'

    try {
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      })
      if (!res.ok) throw new Error(`Errore ${res.status}`)
      await loadSources()
      queryClient.invalidateQueries({ queryKey: ['news'] })
      closeModal()
    } catch {
      alert(t('sources.errorSave'))
    }
  }

  const handleDiscover = async () => {
    if (!discoveryQuery.trim()) return
    setDiscovering(true)
    setDiscoveredFeeds([])
    setSearchedSites([])
    setDiscoveryDone(false)
    try {
      const result = await discoverFeeds(discoveryQuery.trim())
      setDiscoveredFeeds(result.feeds)
      setSearchedSites(result.searched_sites)
      setDiscoveryDone(true)
    } catch {
      alert(t('sources.errorDiscover'))
    } finally {
      setDiscovering(false)
    }
  }

  const addDiscoveredFeed = async (feed: DiscoveredFeed) => {
    setAddingFeed(feed.url)
    try {
      const res = await fetch('/api/sources', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: feed.title,
          feed_url: feed.url,
          source_type: feed.feed_type,
          description: t('sources.discoveredFrom', { url: feed.site_url }),
          update_frequency_minutes: 60,
        }),
      })
      if (!res.ok) throw new Error(`Errore ${res.status}`)
      await loadSources()
      queryClient.invalidateQueries({ queryKey: ['news'] })
      setDiscoveredFeeds((prev) => prev.filter((f) => f.url !== feed.url))
    } catch {
      alert(t('sources.errorAdd'))
    } finally {
      setAddingFeed(null)
    }
  }

  const processFeed = async (id: number) => {
    setProcessing(id)
    try {
      const res = await fetch(`/api/sources/${id}/process`, { method: 'POST' })
      if (!res.ok) throw new Error(`Errore ${res.status}`)
      const data = await res.json()
      alert(data.message ?? '')
      if (data.success) {
        queryClient.invalidateQueries({ queryKey: ['news'] })
      }
      await loadSources()
    } catch {
      alert(t('sources.errorImport'))
    } finally {
      setProcessing(null)
    }
  }

  // Subscribed source IDs for marking catalog results
  const subscribedIds = new Set(sources.map((s) => s.id))

  return (
    <div className="mx-auto max-w-4xl px-4 py-6 md:px-6">
      <div className="mb-6">
        <h1 className="font-serif text-3xl font-bold">{t('sources.title')}</h1>
        <p className="mt-1 text-muted-foreground">{t('sources.description')}</p>
      </div>

      {/* Search bar + Add button */}
      <div className="mb-6 flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={t('sources.searchCatalog')}
            className="pl-10"
          />
        </div>
        <Button onClick={openAddModal}>
          <Plus className="mr-1.5 h-4 w-4" />
          {t('sources.addFeed')}
        </Button>
      </div>

      {/* Catalog search results */}
      {isSearching && (
        <div className="mb-6">
          {catalogLoading && catalogResults.length === 0 ? (
            <div className="space-y-3">
              <Skeleton className="h-20 w-full rounded-lg" />
              <Skeleton className="h-20 w-full rounded-lg" />
            </div>
          ) : catalogResults.length === 0 && !catalogLoading ? (
            <Card>
              <CardContent className="py-8 text-center text-muted-foreground">
                {t('sources.noResults')}
              </CardContent>
            </Card>
          ) : (
            <>
              <h2 className="mb-3 text-sm font-semibold text-muted-foreground">
                {t('sources.catalogResults')} ({catalogTotal})
              </h2>
              <div className="space-y-3">
                {catalogResults.map((source) => {
                  const isSubbed = source.is_subscribed || subscribedIds.has(source.id)
                  return (
                    <Card key={source.id} className="transition-shadow hover:shadow-md">
                      <CardHeader className="pb-2">
                        <div className="flex items-start justify-between gap-4">
                          <div className="min-w-0 flex-1">
                            <CardTitle className="text-base">{source.name}</CardTitle>
                            {source.description && (
                              <p className="mt-0.5 line-clamp-2 text-sm text-muted-foreground">
                                {source.description}
                              </p>
                            )}
                          </div>
                          <Button
                            variant={isSubbed ? 'default' : 'outline'}
                            size="sm"
                            className="shrink-0"
                            onClick={() => !isSubbed && handleSubscribe(source.id)}
                            disabled={isSubbed || subscribing === source.id}
                          >
                            {isSubbed ? (
                              <>
                                <Check className="mr-1.5 h-3.5 w-3.5" />
                                {t('sources.subscribed')}
                              </>
                            ) : subscribing === source.id ? (
                              t('sources.adding')
                            ) : (
                              <>
                                <Plus className="mr-1.5 h-3.5 w-3.5" />
                                {t('sources.subscribe')}
                              </>
                            )}
                          </Button>
                        </div>
                      </CardHeader>
                      <CardContent className="pt-0">
                        <div className="flex flex-wrap items-center gap-1.5">
                          {source.geographic_level && (
                            <Badge variant="secondary" className="text-xs">
                              {source.geographic_level === 'CONTINENTAL'
                                ? 'EU'
                                : source.country_code || source.geographic_level}
                            </Badge>
                          )}
                          {source.tags.map((tag) => (
                            <Badge key={tag} variant="outline" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )
                })}
              </div>

              {catalogHasMore && (
                <div className="mt-4 text-center">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => searchCatalog(debouncedSearch.trim(), catalogOffset)}
                    disabled={catalogLoading}
                  >
                    {catalogLoading ? t('common.loading') : t('sources.loadMore')}
                  </Button>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* Subscribed sources list */}
      {!isSearching && (
        <>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold">
              {t('sources.yourSources')} {!loading && !error && `(${sources.length})`}
            </h2>
          </div>

          {loading ? (
            <div className="space-y-4">
              {[1, 2].map((i) => (
                <Card key={i}>
                  <CardHeader>
                    <Skeleton className="h-5 w-48" />
                    <Skeleton className="mt-2 h-4 w-32" />
                  </CardHeader>
                  <CardContent>
                    <Skeleton className="h-4 w-full" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : error ? (
            <Card>
              <CardContent className="py-12 text-center">
                <p className="text-destructive">{error}</p>
                <Button variant="outline" className="mt-4" onClick={loadSources}>
                  {t('common.retry')}
                </Button>
              </CardContent>
            </Card>
          ) : sources.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center text-muted-foreground">
                {t('sources.noFeeds')}
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {sources.map((source) => (
                <Card key={source.id}>
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between gap-4">
                      <div className="min-w-0 flex-1">
                        <CardTitle className="text-lg">{source.name}</CardTitle>
                        {source.description && (
                          <p className="mt-1 text-sm text-muted-foreground">
                            {source.description}
                          </p>
                        )}
                      </div>
                      <Badge variant={source.is_active ? 'default' : 'secondary'}>
                        {source.is_active ? t('sources.active') : t('sources.inactive')}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-4 text-sm md:grid-cols-4">
                      <div className="col-span-2 min-w-0">
                        <span className="text-muted-foreground">{t('sources.urlLabel')}</span>
                        <p className="mt-0.5 truncate font-mono text-xs">{source.feed_url}</p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">{t('sources.typeLabel')}</span>
                        <p className="mt-0.5">
                          <Badge variant="outline">{source.source_type}</Badge>
                        </p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">{t('sources.frequencyLabel')}</span>
                        <p className="mt-0.5">{source.update_frequency_minutes} min</p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">{t('sources.lastFetch')}</span>
                        <p className="mt-0.5">
                          {source.last_fetched
                            ? new Date(source.last_fetched).toLocaleString()
                            : t('sources.never')}
                        </p>
                      </div>
                    </div>

                    <Separator className="my-4" />

                    <div className="flex flex-wrap gap-2">
                      {source.is_active && (
                        <Button
                          size="sm"
                          onClick={() => processFeed(source.id)}
                          disabled={processing === source.id}
                        >
                          {processing === source.id
                            ? t('sources.importing')
                            : t('sources.importNews')}
                        </Button>
                      )}
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => openEditModal(source)}
                      >
                        {t('sources.edit')}
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => handleUnsubscribe(source.id)}
                      >
                        {t('sources.unsubscribe')}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </>
      )}

      {/* Add/Edit Modal */}
      {showModal && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
          onClick={closeModal}
        >
          <Card
            className="w-full max-w-lg max-h-[90vh] overflow-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>
                  {editMode ? t('sources.editFeedTitle') : t('sources.addFeedTitle')}
                </CardTitle>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={closeModal}
                  aria-label={t('common.close')}
                >
                  &times;
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Feed discovery inside modal (only for add) */}
              {!editMode && (
                <>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">{t('sources.discoverTitle')}</label>
                    <p className="text-xs text-muted-foreground">{t('sources.discoverHelp')}</p>
                    <div className="flex gap-2">
                      <Input
                        value={discoveryQuery}
                        onChange={(e) => setDiscoveryQuery(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleDiscover()}
                        placeholder={t('sources.discoverPlaceholder')}
                        className="flex-1"
                        disabled={discovering}
                      />
                      <Button
                        size="sm"
                        onClick={handleDiscover}
                        disabled={discovering || !discoveryQuery.trim()}
                      >
                        {discovering ? t('sources.discovering') : t('sources.discoverButton')}
                      </Button>
                    </div>

                    {discovering && (
                      <div className="space-y-2">
                        <Skeleton className="h-12 w-full" />
                        <Skeleton className="h-12 w-full" />
                      </div>
                    )}

                    {discoveryDone && !discovering && discoveredFeeds.length === 0 && (
                      <p className="text-sm text-muted-foreground">{t('sources.noFeedsFound')}</p>
                    )}

                    {discoveredFeeds.length > 0 && (
                      <div className="space-y-2">
                        {searchedSites.length > 1 && (
                          <p className="text-xs text-muted-foreground">
                            {t('sources.sitesAnalyzed', { count: searchedSites.length })}
                          </p>
                        )}
                        {discoveredFeeds.map((feed) => (
                          <div
                            key={feed.url}
                            className="flex items-center justify-between gap-3 rounded-lg border p-2"
                          >
                            <div className="min-w-0 flex-1">
                              <div className="flex items-center gap-2">
                                <p className="truncate text-sm font-medium">{feed.title}</p>
                                <Badge variant="outline" className="text-xs">
                                  {feed.feed_type}
                                </Badge>
                              </div>
                              <p className="truncate font-mono text-xs text-muted-foreground">
                                {feed.url}
                              </p>
                            </div>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => addDiscoveredFeed(feed)}
                              disabled={addingFeed === feed.url}
                            >
                              {addingFeed === feed.url ? t('sources.adding') : t('sources.add')}
                            </Button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  <Separator />
                  <p className="text-xs text-muted-foreground">{t('sources.discoverHelp')}</p>
                </>
              )}

              <div className="space-y-2">
                <label className="text-sm font-medium">{t('sources.nameLabel')}</label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder={t('sources.namePlaceholder')}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">{t('sources.descriptionLabel')}</label>
                <textarea
                  className="flex min-h-20 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder={t('sources.descriptionPlaceholder')}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">{t('sources.urlFeedLabel')}</label>
                <Input
                  type="url"
                  value={formData.feed_url}
                  onChange={(e) => setFormData({ ...formData, feed_url: e.target.value })}
                  placeholder={t('sources.urlFeedPlaceholder')}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">{t('sources.typeRequired')}</label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  value={formData.source_type}
                  onChange={(e) => setFormData({ ...formData, source_type: e.target.value })}
                >
                  <option value="RSS">RSS</option>
                  <option value="Atom">Atom</option>
                  <option value="WebScraping">Web Scraping</option>
                  <option value="API">API</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">{t('sources.categoryLabel')}</label>
                <Input
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  placeholder={t('sources.categoryPlaceholder')}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">{t('sources.frequencyRequired')}</label>
                <Input
                  type="number"
                  value={formData.update_frequency_minutes}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      update_frequency_minutes: parseInt(e.target.value) || 60,
                    })
                  }
                  min="1"
                />
              </div>

              {editMode && (
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="is-active"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    className="h-4 w-4 rounded border-input"
                  />
                  <label htmlFor="is-active" className="text-sm font-medium">
                    {t('sources.feedActive')}
                  </label>
                </div>
              )}

              <Separator />

              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={closeModal}>
                  {t('common.cancel')}
                </Button>
                <Button onClick={saveSource}>
                  {editMode ? t('sources.update') : t('sources.add')}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
