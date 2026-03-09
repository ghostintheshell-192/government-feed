import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useQuery, useQueryClient } from '@tanstack/react-query'
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
import { ArticleContent } from '@/components/article-content'
import { useReadStatus } from '@/lib/use-read-status'

export default function NewsDetail() {
  const { id } = useParams<{ id: string }>()
  const newsId = Number(id)
  const { markAsRead } = useReadStatus()
  const queryClient = useQueryClient()
  const { t, i18n } = useTranslation()

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

  const handleFetchContent = async (force: boolean = false) => {
    if (!item) return
    setFetchingContent(true)
    try {
      const data = await fetchNewsContent(item.id, force)
      if (data.success && data.content) {
        updateItem({ content: data.content })
      } else {
        alert(data.message || t('newsDetail.errorFetchContent'))
      }
    } catch {
      alert(t('newsDetail.errorFetchContentGeneric'))
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
        alert(data.message || t('common.errorSummary'))
      }
    } catch {
      alert(t('common.errorAiConnection'))
    } finally {
      setSummarizing(false)
    }
  }

  if (isLoading) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-6 md:px-6">
        <Skeleton className="mb-6 h-8 w-48" />
        <Skeleton className="mb-4 h-10 w-3/4" />
        <Skeleton className="mb-2 h-5 w-1/4" />
        <Skeleton className="mt-6 h-40 w-full" />
      </div>
    )
  }

  if (error || !item) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-6 md:px-6">
        <div className="py-16 text-center">
          <h2 className="font-serif text-xl font-semibold text-muted-foreground">
            {t('common.notFound')}
          </h2>
          <p className="mt-2 text-muted-foreground">
            {t('common.notFoundDesc')}
          </p>
        </div>
      </div>
    )
  }

  const hasFullContent = item.content && item.content.length > 500

  return (
    <div className="mx-auto max-w-4xl px-4 py-6 md:px-6">
      <article>
        <h1 className="font-serif text-3xl font-bold leading-tight">{item.title}</h1>

        <div className="mt-3 flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
          {sourceName && <Badge variant="secondary">{sourceName}</Badge>}
          <span>
            {t('newsDetail.publishedAt')}{' '}
            {new Date(item.published_at).toLocaleDateString(i18n.language, {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
        </div>

        {item.summary && (
          <Card className="mt-6 border-primary/20 bg-primary/5">
            <CardContent className="pt-6">
              <p className="mb-2 text-sm font-semibold text-primary">
                {t('newsDetail.aiSummary')}
              </p>
              <p className="leading-relaxed text-foreground/90">
                {item.summary}
              </p>
            </CardContent>
          </Card>
        )}

        <Separator className="my-6" />

        {hasFullContent ? (
          <ArticleContent content={item.content!} />
        ) : item.content ? (
          <div>
            <p className="leading-relaxed text-muted-foreground">
              {item.content}
            </p>
            <p className="mt-4 text-sm italic text-muted-foreground">
              {t('newsDetail.partialContent')}
            </p>
          </div>
        ) : (
          <div className="py-8 text-center text-muted-foreground">
            <p>{t('newsDetail.noContent')}</p>
            <p className="mt-1 text-sm">
              {t('newsDetail.noContentHelp')}
            </p>
          </div>
        )}

        <Separator className="my-6" />

        <div className="flex flex-wrap gap-3">
          {!hasFullContent ? (
            <Button
              variant="outline"
              onClick={() => handleFetchContent()}
              disabled={fetchingContent}
            >
              {fetchingContent ? t('common.loading') : t('newsDetail.fetchContent')}
            </Button>
          ) : (
            <Button
              variant="ghost"
              onClick={() => handleFetchContent(true)}
              disabled={fetchingContent}
            >
              {fetchingContent ? t('common.loading') : t('newsDetail.updateContent')}
            </Button>
          )}

          {features?.ai_enabled && (
            <Button
              variant={item.summary ? 'ghost' : 'outline'}
              onClick={handleSummarize}
              disabled={summarizing}
            >
              {summarizing
                ? t('common.generating')
                : item.summary
                  ? t('newsDetail.regenerateSummary')
                  : t('common.aiSummarize')}
            </Button>
          )}

          {item.external_id && (
            <Button
              variant="ghost"
              onClick={() => window.open(item.external_id!, '_blank')}
            >
              {t('common.openOriginal')}
            </Button>
          )}
        </div>
      </article>
    </div>
  )
}
