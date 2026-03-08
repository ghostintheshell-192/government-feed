import { useEffect, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'
import { discoverFeeds, type DiscoveredFeed } from '@/lib/api'

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

export default function Sources() {
  const queryClient = useQueryClient()
  const { t } = useTranslation()
  const [sources, setSources] = useState<Source[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editMode, setEditMode] = useState(false)
  const [editId, setEditId] = useState<number | null>(null)
  const [processing, setProcessing] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [formData, setFormData] = useState<SourceFormData>({ ...emptyForm })
  const [discoveryQuery, setDiscoveryQuery] = useState('')
  const [discovering, setDiscovering] = useState(false)
  const [discoveredFeeds, setDiscoveredFeeds] = useState<DiscoveredFeed[]>([])
  const [searchedSites, setSearchedSites] = useState<string[]>([])
  const [discoveryDone, setDiscoveryDone] = useState(false)
  const [addingFeed, setAddingFeed] = useState<string | null>(null)

  useEffect(() => {
    loadSources()
  }, [])

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

  const openAddModal = () => {
    setEditMode(false)
    setEditId(null)
    setFormData({ ...emptyForm })
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
      closeModal()
    } catch {
      alert(t('sources.errorSave'))
    }
  }

  const deleteSource = async (id: number) => {
    if (!confirm(t('sources.confirmDelete'))) return
    try {
      const res = await fetch(`/api/sources/${id}`, { method: 'DELETE' })
      if (!res.ok) throw new Error(`Errore ${res.status}`)
      await loadSources()
    } catch {
      alert(t('sources.errorDelete'))
    }
  }

  const toggleActive = async (source: Source) => {
    try {
      const res = await fetch(`/api/sources/${source.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...source, is_active: !source.is_active }),
      })
      if (!res.ok) throw new Error(`Errore ${res.status}`)
      await loadSources()
    } catch {
      alert(t('sources.errorToggle'))
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

  return (
    <div className="mx-auto max-w-5xl px-4 py-6 md:px-6">
      <div className="mb-6">
        <h1 className="font-serif text-3xl font-bold">{t('sources.title')}</h1>
        <p className="mt-1 text-muted-foreground">
          {t('sources.description')}
        </p>
      </div>

      <Card className="mb-6">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">{t('sources.discoverTitle')}</CardTitle>
          <p className="text-sm text-muted-foreground">
            {t('sources.discoverHelp')}
          </p>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <Input
              value={discoveryQuery}
              onChange={(e) => setDiscoveryQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleDiscover()}
              placeholder={t('sources.discoverPlaceholder')}
              className="flex-1"
              disabled={discovering}
            />
            <Button onClick={handleDiscover} disabled={discovering || !discoveryQuery.trim()}>
              {discovering ? t('sources.discovering') : t('sources.discoverButton')}
            </Button>
          </div>

          {discovering && (
            <div className="mt-4 space-y-2">
              <Skeleton className="h-16 w-full" />
              <Skeleton className="h-16 w-full" />
            </div>
          )}

          {discoveryDone && !discovering && discoveredFeeds.length === 0 && (
            <p className="mt-4 text-sm text-muted-foreground">
              {t('sources.noFeedsFound')}
            </p>
          )}

          {discoveredFeeds.length > 0 && (
            <div className="mt-4 space-y-3">
              {searchedSites.length > 1 && (
                <p className="text-xs text-muted-foreground">
                  {t('sources.sitesAnalyzed', { count: searchedSites.length })}
                </p>
              )}
              {discoveredFeeds.map((feed) => (
                <div
                  key={feed.url}
                  className="flex items-center justify-between gap-4 rounded-lg border p-3"
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <p className="truncate font-medium">{feed.title}</p>
                      <Badge variant="outline">{feed.feed_type}</Badge>
                      <Badge variant="secondary">{feed.entry_count} {t('sources.articles')}</Badge>
                    </div>
                    <p className="mt-0.5 truncate font-mono text-xs text-muted-foreground">
                      {feed.url}
                    </p>
                  </div>
                  <Button
                    size="sm"
                    onClick={() => addDiscoveredFeed(feed)}
                    disabled={addingFeed === feed.url}
                  >
                    {addingFeed === feed.url ? t('sources.adding') : t('sources.add')}
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-lg font-semibold">
          {t('sources.feedsTitle')} {!loading && !error && `(${sources.length})`}
        </h2>
        <Button onClick={openAddModal}>{t('sources.addFeed')}</Button>
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
                  <Badge
                    variant={source.is_active ? 'default' : 'secondary'}
                  >
                    {source.is_active ? t('sources.active') : t('sources.inactive')}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4 text-sm md:grid-cols-4">
                  <div className="col-span-2 min-w-0">
                    <span className="text-muted-foreground">{t('sources.urlLabel')}</span>
                    <p className="mt-0.5 truncate font-mono text-xs">
                      {source.feed_url}
                    </p>
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
                    variant="outline"
                    size="sm"
                    onClick={() => toggleActive(source)}
                  >
                    {source.is_active ? t('sources.deactivate') : t('sources.activate')}
                  </Button>
                  {!source.is_active && (
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => deleteSource(source.id)}
                    >
                      {t('sources.delete')}
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

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
              <div className="space-y-2">
                <label className="text-sm font-medium">{t('sources.nameLabel')}</label>
                <Input
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  placeholder={t('sources.namePlaceholder')}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">{t('sources.descriptionLabel')}</label>
                <textarea
                  className="flex min-h-20 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                  placeholder={t('sources.descriptionPlaceholder')}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">{t('sources.urlFeedLabel')}</label>
                <Input
                  type="url"
                  value={formData.feed_url}
                  onChange={(e) =>
                    setFormData({ ...formData, feed_url: e.target.value })
                  }
                  placeholder={t('sources.urlFeedPlaceholder')}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">{t('sources.typeRequired')}</label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  value={formData.source_type}
                  onChange={(e) =>
                    setFormData({ ...formData, source_type: e.target.value })
                  }
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
                  onChange={(e) =>
                    setFormData({ ...formData, category: e.target.value })
                  }
                  placeholder={t('sources.categoryPlaceholder')}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">
                  {t('sources.frequencyRequired')}
                </label>
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
                    onChange={(e) =>
                      setFormData({ ...formData, is_active: e.target.checked })
                    }
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
