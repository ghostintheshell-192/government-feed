import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { summarizeNews } from '@/lib/api'
import { highlightMatches } from '@/lib/highlight'
import { extractSnippet } from '@/lib/search-snippet'
import type { NewsItem } from '@/lib/types'

interface NewsCardProps {
  item: NewsItem
  sourceName?: string
  isRead: boolean
  aiEnabled: boolean
  searchTerm?: string
  onRead: (id: number) => void
  onSummaryUpdate: (id: number, summary: string) => void
}

/** Strip HTML tags to get plain text for preview snippets. */
function stripHtml(html: string): string {
  return html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim()
}

export function NewsCard({
  item,
  sourceName,
  isRead,
  aiEnabled,
  searchTerm,
  onRead,
  onSummaryUpdate,
}: NewsCardProps) {
  const [summarizing, setSummarizing] = useState(false)

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

  const plainContent = item.content ? stripHtml(item.content) : null
  const contentSnippet = plainContent
    ? extractSnippet(plainContent, searchTerm)
    : null
  const preview =
    searchTerm && contentSnippet
      ? contentSnippet
      : item.summary || contentSnippet

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
            <CardTitle className="font-serif text-lg leading-snug">
              <Link
                to={`/news/${item.id}`}
                className="transition-colors hover:text-primary hover:underline"
              >
                {highlightMatches(item.title, searchTerm)}
              </Link>
            </CardTitle>
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
        {preview && (
          <p className="text-sm leading-relaxed text-muted-foreground">
            {highlightMatches(preview, searchTerm)}
          </p>
        )}

        <div className="mt-3 flex flex-wrap gap-2">
          <Button variant="outline" size="sm" asChild>
            <Link
              to={`/news/${item.id}`}
              onClick={(e) => e.stopPropagation()}
            >
              Leggi articolo
            </Link>
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
