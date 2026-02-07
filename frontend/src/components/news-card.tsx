import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { summarizeNews } from '@/lib/api'
import type { NewsItem } from '@/lib/types'

interface NewsCardProps {
  item: NewsItem
  sourceName?: string
  isRead: boolean
  aiEnabled: boolean
  onRead: (id: number) => void
  onSummaryUpdate: (id: number, summary: string) => void
}

export function NewsCard({
  item,
  sourceName,
  isRead,
  aiEnabled,
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
      {(preview || (aiEnabled && !item.summary)) && (
        <CardContent className="pt-0">
          {preview && (
            <p className="text-sm leading-relaxed text-muted-foreground">
              {preview}
            </p>
          )}
          {aiEnabled && !item.summary && (
            <Button
              variant="outline"
              size="sm"
              className="mt-3"
              onClick={handleSummarize}
              disabled={summarizing}
            >
              {summarizing ? 'Generando...' : 'Riassumi con AI'}
            </Button>
          )}
        </CardContent>
      )}
    </Card>
  )
}
