import { useEffect, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'

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
  const [sources, setSources] = useState<Source[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editMode, setEditMode] = useState(false)
  const [editId, setEditId] = useState<number | null>(null)
  const [processing, setProcessing] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [formData, setFormData] = useState<SourceFormData>({ ...emptyForm })

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
      setError('Impossibile caricare i feed. Verifica che il backend sia attivo.')
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
      alert('Nome e URL Feed sono obbligatori')
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
      alert('Errore nel salvataggio del feed.')
    }
  }

  const deleteSource = async (id: number) => {
    if (!confirm('Eliminare questo feed?')) return
    try {
      const res = await fetch(`/api/sources/${id}`, { method: 'DELETE' })
      if (!res.ok) throw new Error(`Errore ${res.status}`)
      await loadSources()
    } catch {
      alert("Errore nell'eliminazione del feed.")
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
      alert('Errore nel cambio di stato del feed.')
    }
  }

  const processFeed = async (id: number) => {
    setProcessing(id)
    try {
      const res = await fetch(`/api/sources/${id}/process`, { method: 'POST' })
      if (!res.ok) throw new Error(`Errore ${res.status}`)
      const data = await res.json()
      alert(data.message)
      if (data.success) {
        queryClient.invalidateQueries({ queryKey: ['news'] })
      }
      await loadSources()
    } catch {
      alert("Errore nell'importazione delle notizie.")
    } finally {
      setProcessing(null)
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-6 md:px-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Gestione Sources</h1>
        <p className="mt-1 text-muted-foreground">
          Configura e gestisci i feed istituzionali
        </p>
      </div>

      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-lg font-semibold">
          Feed {!loading && !error && `(${sources.length})`}
        </h2>
        <Button onClick={openAddModal}>+ Aggiungi Feed</Button>
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
              Riprova
            </Button>
          </CardContent>
        </Card>
      ) : sources.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            Nessun feed configurato. Aggiungi il tuo primo feed per iniziare.
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
                    {source.is_active ? 'Attivo' : 'Inattivo'}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4 text-sm md:grid-cols-4">
                  <div className="col-span-2 min-w-0">
                    <span className="text-muted-foreground">URL</span>
                    <p className="mt-0.5 truncate font-mono text-xs">
                      {source.feed_url}
                    </p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Tipo</span>
                    <p className="mt-0.5">
                      <Badge variant="outline">{source.source_type}</Badge>
                    </p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Frequenza</span>
                    <p className="mt-0.5">{source.update_frequency_minutes} min</p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Ultima fetch</span>
                    <p className="mt-0.5">
                      {source.last_fetched
                        ? new Date(source.last_fetched).toLocaleString('it-IT')
                        : 'Mai'}
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
                        ? 'Importando...'
                        : 'Importa Notizie'}
                    </Button>
                  )}
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => openEditModal(source)}
                  >
                    Modifica
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => toggleActive(source)}
                  >
                    {source.is_active ? 'Disattiva' : 'Attiva'}
                  </Button>
                  {!source.is_active && (
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => deleteSource(source.id)}
                    >
                      Elimina
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
                  {editMode ? 'Modifica Feed' : 'Aggiungi Nuovo Feed'}
                </CardTitle>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={closeModal}
                  aria-label="Chiudi"
                >
                  &times;
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Nome *</label>
                <Input
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  placeholder="Es: Governo Italiano"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Descrizione</label>
                <textarea
                  className="flex min-h-20 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                  placeholder="Descrizione opzionale"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">URL Feed *</label>
                <Input
                  type="url"
                  value={formData.feed_url}
                  onChange={(e) =>
                    setFormData({ ...formData, feed_url: e.target.value })
                  }
                  placeholder="https://example.com/feed.rss"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Tipo *</label>
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
                <label className="text-sm font-medium">Categoria</label>
                <Input
                  value={formData.category}
                  onChange={(e) =>
                    setFormData({ ...formData, category: e.target.value })
                  }
                  placeholder="Es: Governo Centrale"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">
                  Frequenza Aggiornamento (minuti) *
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
                    Feed Attivo
                  </label>
                </div>
              )}

              <Separator />

              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={closeModal}>
                  Annulla
                </Button>
                <Button onClick={saveSource}>
                  {editMode ? 'Aggiorna' : 'Aggiungi'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
