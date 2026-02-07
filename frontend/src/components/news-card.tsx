import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { fetchNewsContent, summarizeNews } from '@/lib/api'
import type { NewsItem } from '@/lib/types'

interface NewsCardProps {
  item: NewsItem
  sourceName?: string
  isRead: boolean
  aiEnabled: boolean
  onRead: (id: number) => void
  onSummaryUpdate: (id: number, summary: string) => void
  onContentUpdate: (id: number, content: string) => void
}

export function NewsCard({
  item,
  sourceName,
  isRead,
  aiEnabled,
  onRead,
  onSummaryUpdate,
  onContentUpdate,
}: NewsCardProps) {
  const [summarizing, setSummarizing] = useState(false)
  const [fetchingContent, setFetchingContent] = useState(false)
  const [expanded, setExpanded] = useState(false)

  const handleClick = () => {
    if (!isRead) onRead(item.id)
  }

  const handleSummarize = async (e: React.MouseEvent) => {
    e.stopPropagation()
    setSummarizing(true)
    try {
      const data = await summarizeNews(item.id)
      if (data.success) {
        onSummaryUpdate(item.id, data.summary)
      } else {
        alert(data.message || 'Errore nella generazione del riassunto')
      }
    } catch {
      alert('Errore di connessione al servizio AI')
    } finally {
      setSummarizing(false)
    }
  }

  const handleShowContent = async (e: React.MouseEvent) => {
    e.stopPropagation()

    // If we already have full content, just toggle
    if (item.content && item.content.length > 500) {
      setExpanded(!expanded)
      return
    }

    setFetchingContent(true)
    try {
      const data = await fetchNewsContent(item.id)
      if (data.success && data.content) {
        onContentUpdate(item.id, data.content)
        setExpanded(true)
      } else {
        alert(data.message || 'Impossibile recuperare il contenuto')
      }
    } catch {
      alert('Errore nel recupero del contenuto')
    } finally {
      setFetchingContent(false)
    }
  }

  const hasFullContent = item.content && item.content.length > 500
  const preview = item.summary || (item.content ? item.content.slice(0, 200) + (item.content.length > 200 ? '...' : '') : null)

  return (
    <Card
      className="cursor-pointer transition-shadow hover:shadow-md"
      onClick={handleClick}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start gap-3">
          {!isRead && (
            <span className="mt-2 h-2.5 w-2.5 shrink-0 rounded-full bg-blue-500" />
          )}
          <div className="flex-1 space-y-1.5">
            <CardTitle className="text-lg leading-snug">{item.title}</CardTitle>
            <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
              {sourceName && <Badge variant="secondary">{sourceName}</Badge>}
              <span>
                {new Date(item.published_at).toLocaleDateString('it-IT', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </span>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        {!expanded && preview && (
          <p className="text-sm leading-relaxed text-muted-foreground">
            {preview}
          </p>
        )}

        {expanded && item.content && (
          <>
            <Separator className="my-3" />
            <p className="whitespace-pre-line text-sm leading-relaxed">
              {item.content}
            </p>
          </>
        )}

        <div className="mt-3 flex flex-wrap gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleShowContent}
            disabled={fetchingContent}
          >
            {fetchingContent
              ? 'Caricamento...'
              : expanded
                ? 'Nascondi articolo'
                : hasFullContent
                  ? 'Mostra articolo'
                  : 'Scarica articolo'}
          </Button>

          {aiEnabled && !item.summary && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleSummarize}
              disabled={summarizing}
            >
              {summarizing ? 'Generando...' : 'Riassumi con AI'}
            </Button>
          )}

          {item.external_id && (
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation()
                window.open(item.external_id!, '_blank')
              }}
            >
              Apri originale
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
