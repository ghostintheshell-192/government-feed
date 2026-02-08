import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'
import {
  fetchNewsById,
  fetchSources,
  fetchFeatures,
  fetchNewsContent,
  summarizeNews,
} from '@/lib/api'
import type { NewsItem } from '@/lib/types'
import { useReadStatus } from '@/lib/use-read-status'

export default function NewsDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const newsId = Number(id)
  const { markAsRead } = useReadStatus()
  const queryClient = useQueryClient()

  const [summarizing, setSummarizing] = useState(false)
  const [fetchingContent, setFetchingContent] = useState(false)

  const {
    data: item,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['news-detail', newsId],
    queryFn: () => fetchNewsById(newsId),
    enabled: !isNaN(newsId),
  })

  const { data: sources = [] } = useQuery({
    queryKey: ['sources'],
    queryFn: fetchSources,
  })

  const { data: features } = useQuery({
    queryKey: ['features'],
    queryFn: fetchFeatures,
  })

  useEffect(() => {
    if (item) {
      markAsRead(item.id)
    }
  }, [item, markAsRead])

  const sourceName = sources.find((s) => s.id === item?.source_id)?.name

  const updateItem = (updates: Partial<NewsItem>) => {
    queryClient.setQueryData<NewsItem>(
      ['news-detail', newsId],
      (old) => (old ? { ...old, ...updates } : old),
    )
    queryClient.invalidateQueries({ queryKey: ['news'] })
  }

  const handleFetchContent = async () => {
    if (!item) return
    setFetchingContent(true)
    try {
      const data = await fetchNewsContent(item.id)
      if (data.success && data.content) {
        updateItem({ content: data.content })
      } else {
        alert(data.message || 'Impossibile recuperare il contenuto')
      }
    } catch {
      alert('Errore nel recupero del contenuto')
    } finally {
      setFetchingContent(false)
    }
  }

  const handleSummarize = async () => {
    if (!item) return
    setSummarizing(true)
    try {
      const data = await summarizeNews(item.id)
      if (data.success) {
        updateItem({ summary: data.summary })
      } else {
        alert(data.message || 'Errore nella generazione del riassunto')
      }
    } catch {
      alert('Errore di connessione al servizio AI')
    } finally {
      setSummarizing(false)
    }
  }

  if (isLoading) {
    return (
      <div className="mx-auto max-w-4xl p-6">
        <Skeleton className="mb-6 h-8 w-48" />
        <Skeleton className="mb-4 h-10 w-3/4" />
        <Skeleton className="mb-2 h-5 w-1/4" />
        <Skeleton className="mt-6 h-40 w-full" />
      </div>
    )
  }

  if (error || !item) {
    return (
      <div className="mx-auto max-w-4xl p-6">
        <Button variant="ghost" onClick={() => navigate('/')}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Torna alla dashboard
        </Button>
        <div className="py-16 text-center">
          <h2 className="text-xl font-semibold text-muted-foreground">
            Articolo non trovato
          </h2>
          <p className="mt-2 text-muted-foreground">
            L&apos;articolo richiesto non esiste o non è più disponibile.
          </p>
        </div>
      </div>
    )
  }

  const hasFullContent = item.content && item.content.length > 500

  return (
    <div className="mx-auto max-w-4xl p-6">
      <Button
        variant="ghost"
        className="mb-6"
        onClick={() => navigate('/')}
      >
        <ArrowLeft className="mr-2 h-4 w-4" />
        Torna alla dashboard
      </Button>

      <article>
        <h1 className="text-3xl font-bold leading-tight">{item.title}</h1>

        <div className="mt-3 flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
          {sourceName && <Badge variant="secondary">{sourceName}</Badge>}
          <span>
            Pubblicato il{' '}
            {new Date(item.published_at).toLocaleDateString('it-IT', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
        </div>

        {item.summary && (
          <Card className="mt-6 border-blue-200 bg-blue-50">
            <CardContent className="pt-6">
              <p className="mb-2 text-sm font-semibold text-blue-700">
                Riassunto AI
              </p>
              <p className="leading-relaxed text-blue-900">{item.summary}</p>
            </CardContent>
          </Card>
        )}

        <Separator className="my-6" />

        {hasFullContent ? (
          <div className="whitespace-pre-line leading-relaxed">
            {item.content}
          </div>
        ) : item.content ? (
          <div>
            <p className="leading-relaxed text-muted-foreground">
              {item.content}
            </p>
            <p className="mt-4 text-sm italic text-muted-foreground">
              Il contenuto completo non è ancora stato scaricato.
            </p>
          </div>
        ) : (
          <div className="py-8 text-center text-muted-foreground">
            <p>Contenuto non disponibile.</p>
            <p className="mt-1 text-sm">
              Usa il pulsante &quot;Scarica contenuto&quot; per recuperare
              l&apos;articolo completo.
            </p>
          </div>
        )}

        <Separator className="my-6" />

        <div className="flex flex-wrap gap-3">
          {!hasFullContent && (
            <Button
              variant="outline"
              onClick={handleFetchContent}
              disabled={fetchingContent}
            >
              {fetchingContent ? 'Caricamento...' : 'Scarica contenuto'}
            </Button>
          )}

          {features?.ai_enabled && !item.summary && (
            <Button
              variant="outline"
              onClick={handleSummarize}
              disabled={summarizing}
            >
              {summarizing ? 'Generando...' : 'Riassumi con AI'}
            </Button>
          )}

          {item.external_id && (
            <Button
              variant="ghost"
              onClick={() => window.open(item.external_id!, '_blank')}
            >
              Apri originale
            </Button>
          )}
        </div>
      </article>
    </div>
  )
}
