import { useEffect, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import {
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Code,
  Copy,
  Database,
  Download,
  FileWarning,
  RefreshCw,
  Search,
  Trash2,
  Wrench,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import {
  bulkFetchContent,
  cleanupByPattern,
  cleanupHtmlResidue,
  cleanupOrphans,
  fetchGlobalStats,
  fetchQualityReport,
  fetchSourcePreview,
  fetchSourceStats,
  fetchSources,
  purgeSource,
  reimportSource,
} from '@/lib/api'
import type {
  BulkFetchProgress,
  BulkFetchResult,
  CleanupResult,
  GlobalStats,
  HtmlResidueResult,
  NewsPreview,
  QualityReport,
  ReimportResult,
  Source,
  SourceStats,
} from '@/lib/types'

// ---------------------------------------------------------------------------
// Shared small components
// ---------------------------------------------------------------------------

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border bg-card p-4">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="text-2xl font-bold tabular-nums">{value}</p>
    </div>
  )
}

function IssueSection({
  title,
  icon,
  count,
  children,
}: {
  title: string
  icon: React.ReactNode
  count: number
  children: React.ReactNode
}) {
  const [open, setOpen] = useState(false)

  return (
    <div className="rounded-md border">
      <button
        type="button"
        onClick={() => count > 0 && setOpen(!open)}
        className="flex w-full items-center gap-3 px-4 py-3 text-left text-sm hover:bg-accent/50"
      >
        {icon}
        <span className="flex-1 font-medium">{title}</span>
        {count === 0 ? (
          <CheckCircle2 className="h-4 w-4 text-green-600" />
        ) : (
          <>
            <Badge variant="destructive">{count}</Badge>
            {open ? (
              <ChevronDown className="h-4 w-4 text-muted-foreground" />
            ) : (
              <ChevronRight className="h-4 w-4 text-muted-foreground" />
            )}
          </>
        )}
      </button>
      {open && count > 0 && (
        <div className="border-t px-4 py-2">
          {children}
        </div>
      )}
    </div>
  )
}

function ActionFeedback({ result }: { result: string | null }) {
  if (!result) return null
  return (
    <p className="mt-2 rounded-md border bg-muted/50 px-3 py-2 text-sm">
      {result}
    </p>
  )
}

// ---------------------------------------------------------------------------
// Section type
// ---------------------------------------------------------------------------

type SectionId = 'articles' | 'quality' | 'actions' | 'inspector'

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export default function Admin() {
  const { t } = useTranslation()
  const queryClient = useQueryClient()

  // Active accordion section
  const [activeSection, setActiveSection] = useState<SectionId | null>(null)

  // Global data
  const [stats, setStats] = useState<GlobalStats | null>(null)
  const [quality, setQuality] = useState<QualityReport | null>(null)
  const [sources, setSources] = useState<Source[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Source inspector
  const [inspectSourceId, setInspectSourceId] = useState<number | null>(null)
  const [sourceStats, setSourceStats] = useState<SourceStats | null>(null)
  const [sourcePreview, setSourcePreview] = useState<NewsPreview[]>([])
  const [inspectLoading, setInspectLoading] = useState(false)

  // Actions state
  const [actionSourceId, setActionSourceId] = useState<number | null>(null)
  const [actionBusy, setActionBusy] = useState(false)
  const [actionResult, setActionResult] = useState<string | null>(null)

  // Pattern cleanup
  const [patternField, setPatternField] = useState<'title' | 'content'>('title')
  const [patternText, setPatternText] = useState('')
  const [patternSourceId, setPatternSourceId] = useState<number | undefined>(undefined)
  const [patternResult, setPatternResult] = useState<string | null>(null)

  // Bulk fetch progress
  const [fetchProgress, setFetchProgress] = useState<BulkFetchProgress | null>(null)

  // HTML / orphan cleanup
  const [htmlResult, setHtmlResult] = useState<string | null>(null)
  const [orphanResult, setOrphanResult] = useState<string | null>(null)

  // ---------------------------------------------------------------------------
  // Data loading
  // ---------------------------------------------------------------------------

  useEffect(() => {
    loadAll()
  }, [])

  async function loadAll() {
    setLoading(true)
    setError(null)
    try {
      const [s, st, q] = await Promise.all([
        fetchSources(),
        fetchGlobalStats(),
        fetchQualityReport(),
      ])
      setSources(s)
      setStats(st)
      setQuality(q)
    } catch {
      setError(t('admin.errorLoad'))
    } finally {
      setLoading(false)
    }
  }

  // ---------------------------------------------------------------------------
  // Handlers (unchanged)
  // ---------------------------------------------------------------------------

  async function inspectSource(sourceId: number) {
    setInspectSourceId(sourceId)
    setInspectLoading(true)
    try {
      const [st, preview] = await Promise.all([
        fetchSourceStats(sourceId),
        fetchSourcePreview(sourceId, 10),
      ])
      setSourceStats(st)
      setSourcePreview(preview)
    } catch {
      setSourceStats(null)
      setSourcePreview([])
    } finally {
      setInspectLoading(false)
    }
  }

  async function handlePurge() {
    if (!actionSourceId) return
    const name = sources.find((s) => s.id === actionSourceId)?.name
    if (!window.confirm(t('admin.confirmPurge', { name }))) return

    setActionBusy(true)
    try {
      const result: CleanupResult = await purgeSource(actionSourceId)
      setActionResult(t('admin.purgeResult', { count: result.deleted }))
      await loadAll()
      queryClient.invalidateQueries({ queryKey: ['news'] })
    } catch {
      setActionResult(t('admin.errorAction'))
    } finally {
      setActionBusy(false)
    }
  }

  async function handleReimport() {
    if (!actionSourceId) return
    const name = sources.find((s) => s.id === actionSourceId)?.name
    if (!window.confirm(t('admin.confirmReimport', { name }))) return

    setActionBusy(true)
    try {
      const result: ReimportResult = await reimportSource(actionSourceId)
      setActionResult(
        t('admin.reimportResult', { purged: result.purged, imported: result.imported })
      )
      await loadAll()
      queryClient.invalidateQueries({ queryKey: ['news'] })
    } catch {
      setActionResult(t('admin.errorAction'))
    } finally {
      setActionBusy(false)
    }
  }

  async function handleBulkFetch() {
    if (!actionSourceId) return
    const name = sources.find((s) => s.id === actionSourceId)?.name
    if (!window.confirm(t('admin.confirmBulkFetch', { name }))) return

    setActionBusy(true)
    setFetchProgress(null)
    try {
      const result: BulkFetchResult = await bulkFetchContent(
        actionSourceId,
        false,
        (progress) => setFetchProgress(progress),
      )
      setFetchProgress(null)
      setActionResult(
        t('admin.bulkFetchResult', {
          fetched: result.fetched,
          skipped: result.skipped,
          failed: result.failed,
        })
      )
      await loadAll()
      queryClient.invalidateQueries({ queryKey: ['news'] })
    } catch {
      setFetchProgress(null)
      setActionResult(t('admin.errorAction'))
    } finally {
      setActionBusy(false)
    }
  }

  async function handlePatternCleanup(dryRun: boolean) {
    if (!patternText.trim()) return

    if (!dryRun && !window.confirm(t('admin.confirmPatternDelete'))) return

    setActionBusy(true)
    try {
      const result: CleanupResult = await cleanupByPattern(
        patternField,
        patternText,
        patternSourceId,
        dryRun,
      )
      if (dryRun) {
        setPatternResult(t('admin.patternDryRun', { count: result.matched }))
      } else {
        setPatternResult(t('admin.patternDeleted', { count: result.deleted }))
        await loadAll()
        queryClient.invalidateQueries({ queryKey: ['news'] })
      }
    } catch {
      setPatternResult(t('admin.errorAction'))
    } finally {
      setActionBusy(false)
    }
  }

  async function handleHtmlCleanup() {
    setActionBusy(true)
    try {
      const dryResult: HtmlResidueResult = await cleanupHtmlResidue(true)
      if (dryResult.flagged.length === 0) {
        setHtmlResult(t('admin.htmlNone'))
        setActionBusy(false)
        return
      }

      if (!window.confirm(t('admin.confirmHtmlFix', { count: dryResult.flagged.length }))) {
        setHtmlResult(t('admin.patternDryRun', { count: dryResult.flagged.length }))
        setActionBusy(false)
        return
      }

      const result: HtmlResidueResult = await cleanupHtmlResidue(false)
      setHtmlResult(t('admin.htmlFixed', { count: result.fixed }))
      await loadAll()
    } catch {
      setHtmlResult(t('admin.errorAction'))
    } finally {
      setActionBusy(false)
    }
  }

  async function handleOrphanCleanup() {
    setActionBusy(true)
    try {
      const result: CleanupResult = await cleanupOrphans()
      setOrphanResult(
        result.deleted > 0
          ? t('admin.orphanDeleted', { count: result.deleted })
          : t('admin.orphanNone')
      )
      if (result.deleted > 0) {
        await loadAll()
        queryClient.invalidateQueries({ queryKey: ['news'] })
      }
    } catch {
      setOrphanResult(t('admin.errorAction'))
    } finally {
      setActionBusy(false)
    }
  }

  // ---------------------------------------------------------------------------
  // Loading / error states
  // ---------------------------------------------------------------------------

  if (loading) {
    return (
      <div className="mx-auto space-y-6 px-4 py-6 md:px-6">
        <Skeleton className="h-8 w-48" />
        <div className="grid grid-cols-2 gap-4">
          <Skeleton className="h-24" />
          <Skeleton className="h-24" />
        </div>
        <Skeleton className="h-64" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="mx-auto px-4 py-6 md:px-6">
        <Card>
          <CardContent>
            <p className="text-destructive">{error}</p>
            <Button onClick={loadAll} className="mt-2">
              {t('common.retry')}
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  // ---------------------------------------------------------------------------
  // Derived data
  // ---------------------------------------------------------------------------

  const maxArticles = stats
    ? Math.max(...stats.per_source.map((s) => s.article_count), 1)
    : 1

  const totalIssues = quality
    ? quality.short_content.length +
      quality.long_content.length +
      quality.html_residue.length +
      quality.duplicate_titles.length +
      quality.empty_sources.length
    : 0

  // ---------------------------------------------------------------------------
  // Section definitions
  // ---------------------------------------------------------------------------

  const sections: Array<{
    id: SectionId
    icon: React.ReactNode
    title: string
    description: string
    badge?: number
    badgeVariant?: 'default' | 'secondary' | 'destructive' | 'outline'
    accentColor: string
  }> = [
    {
      id: 'articles',
      icon: <BarChart3 className="h-4 w-4" />,
      title: t('admin.perSourceBreakdown'),
      description: t('admin.articlesDesc'),
      badge: stats?.per_source.length,
      accentColor: 'border-l-primary',
    },
    {
      id: 'quality',
      icon: <Database className="h-4 w-4" />,
      title: t('admin.qualityReport'),
      description: t('admin.qualityDesc'),
      badge: totalIssues > 0 ? totalIssues : undefined,
      badgeVariant: 'destructive',
      accentColor: 'border-l-amber-500',
    },
    {
      id: 'actions',
      icon: <Wrench className="h-4 w-4" />,
      title: t('admin.actions'),
      description: t('admin.actionsDesc'),
      accentColor: 'border-l-red-500',
    },
    {
      id: 'inspector',
      icon: <Search className="h-4 w-4" />,
      title: t('admin.sourceInspector'),
      description: t('admin.inspectorDesc'),
      accentColor: 'border-l-blue-500',
    },
  ]

  function toggleSection(id: SectionId) {
    setActiveSection((prev) => (prev === id ? null : id))
  }

  // ---------------------------------------------------------------------------
  // Section content renderers
  // ---------------------------------------------------------------------------

  function renderArticlesContent() {
    if (!stats || stats.per_source.length === 0) {
      return <p className="text-sm text-muted-foreground">{t('admin.noArticles')}</p>
    }
    return (
      <div className="space-y-2">
        {stats.per_source.map((s) => (
          <div key={s.source_id} className="flex items-center gap-3 text-sm">
            <span className="w-48 shrink-0 truncate" title={s.source_name}>
              {s.source_name}
            </span>
            <div className="flex-1">
              <div
                className="h-4 rounded-sm bg-primary/20"
                style={{
                  width: `${Math.max((s.article_count / maxArticles) * 100, 1)}%`,
                }}
              >
                <div
                  className="h-full rounded-sm bg-primary transition-all"
                  style={{ width: s.article_count > 0 ? '100%' : '0%' }}
                />
              </div>
            </div>
            <span className="w-12 text-right tabular-nums text-muted-foreground">
              {s.article_count}
            </span>
          </div>
        ))}
      </div>
    )
  }

  function renderQualityContent() {
    if (!quality) return null
    return (
      <div className="space-y-2">
        <IssueSection
          title={t('admin.shortContent')}
          icon={<FileWarning className="h-4 w-4 text-amber-500" />}
          count={quality.short_content.length}
        >
          <ul className="space-y-1 py-1">
            {quality.short_content.map((item) => (
              <li key={item.id} className="flex justify-between text-sm">
                <span className="truncate">{item.title}</span>
                <span className="shrink-0 text-muted-foreground">{item.length} chars</span>
              </li>
            ))}
          </ul>
        </IssueSection>

        <IssueSection
          title={t('admin.longContent')}
          icon={<FileWarning className="h-4 w-4 text-amber-500" />}
          count={quality.long_content.length}
        >
          <ul className="space-y-1 py-1">
            {quality.long_content.map((item) => (
              <li key={item.id} className="flex justify-between text-sm">
                <span className="truncate">{item.title}</span>
                <span className="shrink-0 text-muted-foreground">
                  {Math.round(item.length / 1000)}K chars
                </span>
              </li>
            ))}
          </ul>
        </IssueSection>

        <IssueSection
          title={t('admin.htmlResidue')}
          icon={<Code className="h-4 w-4 text-orange-500" />}
          count={quality.html_residue.length}
        >
          <ul className="space-y-1 py-1">
            {quality.html_residue.map((item, i) => (
              <li key={`${item.id}-${item.field}-${i}`} className="flex justify-between text-sm">
                <span className="truncate">{item.title}</span>
                <Badge variant="outline">{item.field}</Badge>
              </li>
            ))}
          </ul>
        </IssueSection>

        <IssueSection
          title={t('admin.duplicateTitles')}
          icon={<Copy className="h-4 w-4 text-blue-500" />}
          count={quality.duplicate_titles.length}
        >
          <ul className="space-y-1 py-1">
            {quality.duplicate_titles.map((item, i) => (
              <li key={i} className="flex justify-between text-sm">
                <span className="truncate">{item.title}</span>
                <span className="shrink-0 text-muted-foreground">&times;{item.count}</span>
              </li>
            ))}
          </ul>
        </IssueSection>

        <IssueSection
          title={t('admin.emptySources')}
          icon={<AlertTriangle className="h-4 w-4 text-red-500" />}
          count={quality.empty_sources.length}
        >
          <ul className="space-y-1 py-1">
            {quality.empty_sources.map((item) => (
              <li key={item.id} className="text-sm">{item.name}</li>
            ))}
          </ul>
        </IssueSection>
      </div>
    )
  }

  function renderActionsContent() {
    return (
      <div className="space-y-6">
        {/* Source purge / reimport */}
        <div>
          <h3 className="mb-3 text-sm font-semibold">{t('admin.sourceActions')}</h3>
          <div className="flex flex-wrap items-end gap-3">
            <div className="min-w-[200px] flex-1">
              <label className="mb-1 block text-sm font-medium">
                {t('admin.selectSource')}
              </label>
              <select
                className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
                value={actionSourceId ?? ''}
                onChange={(e) => {
                  setActionSourceId(e.target.value ? Number(e.target.value) : null)
                  setActionResult(null)
                }}
              >
                <option value="">{t('admin.chooseSource')}</option>
                {sources.map((s) => (
                  <option key={s.id} value={s.id}>{s.name}</option>
                ))}
              </select>
            </div>
            <Button
              variant="destructive"
              size="sm"
              disabled={!actionSourceId || actionBusy}
              onClick={handlePurge}
            >
              <Trash2 className="mr-1 h-3 w-3" />
              {t('admin.purge')}
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={!actionSourceId || actionBusy}
              onClick={handleReimport}
            >
              <RefreshCw className="mr-1 h-3 w-3" />
              {t('admin.reimport')}
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={!actionSourceId || actionBusy}
              onClick={handleBulkFetch}
            >
              <Download className="mr-1 h-3 w-3" />
              {t('admin.bulkFetch')}
            </Button>
          </div>
          <ActionFeedback result={actionResult} />
          {fetchProgress && (
            <div className="mt-3 space-y-1.5">
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span className="truncate pr-4">{fetchProgress.title}</span>
                <span className="shrink-0 tabular-nums">
                  {fetchProgress.current}/{fetchProgress.total}
                </span>
              </div>
              <div className="h-2 w-full overflow-hidden rounded-full bg-primary/20">
                <div
                  className="h-full rounded-full bg-primary transition-[width] duration-300 ease-out"
                  style={{
                    width: `${Math.round((fetchProgress.current / fetchProgress.total) * 100)}%`,
                  }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Pattern cleanup */}
        <div>
          <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold">
            <Search className="h-3.5 w-3.5" />
            {t('admin.patternCleanup')}
          </h3>
          <div className="flex flex-wrap items-end gap-3">
            <div className="w-28">
              <label className="mb-1 block text-sm font-medium">
                {t('admin.field')}
              </label>
              <select
                className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
                value={patternField}
                onChange={(e) => setPatternField(e.target.value as 'title' | 'content')}
              >
                <option value="title">{t('admin.fieldTitle')}</option>
                <option value="content">{t('admin.fieldContent')}</option>
              </select>
            </div>
            <div className="min-w-[200px] flex-1">
              <label className="mb-1 block text-sm font-medium">
                {t('admin.pattern')}
              </label>
              <Input
                type="text"
                value={patternText}
                onChange={(e) => setPatternText(e.target.value)}
                placeholder={t('admin.patternPlaceholder')}
              />
            </div>
            <div className="w-40">
              <label className="mb-1 block text-sm font-medium">
                {t('admin.limitToSource')}
              </label>
              <select
                className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
                value={patternSourceId ?? ''}
                onChange={(e) =>
                  setPatternSourceId(e.target.value ? Number(e.target.value) : undefined)
                }
              >
                <option value="">{t('admin.allSources')}</option>
                {sources.map((s) => (
                  <option key={s.id} value={s.id}>{s.name}</option>
                ))}
              </select>
            </div>
            <Button
              variant="outline"
              size="sm"
              disabled={!patternText.trim() || actionBusy}
              onClick={() => handlePatternCleanup(true)}
            >
              {t('admin.dryRun')}
            </Button>
            <Button
              variant="destructive"
              size="sm"
              disabled={!patternText.trim() || actionBusy}
              onClick={() => handlePatternCleanup(false)}
            >
              {t('admin.delete')}
            </Button>
          </div>
          <ActionFeedback result={patternResult} />
        </div>

        {/* Quick cleanup */}
        <div className="flex flex-wrap gap-3">
          <div className="flex-1">
            <Button
              variant="outline"
              size="sm"
              className="w-full"
              disabled={actionBusy}
              onClick={handleHtmlCleanup}
            >
              <Code className="mr-1 h-3 w-3" />
              {t('admin.fixHtmlResidue')}
            </Button>
            <ActionFeedback result={htmlResult} />
          </div>
          <div className="flex-1">
            <Button
              variant="outline"
              size="sm"
              className="w-full"
              disabled={actionBusy}
              onClick={handleOrphanCleanup}
            >
              <AlertTriangle className="mr-1 h-3 w-3" />
              {t('admin.cleanupOrphans')}
            </Button>
            <ActionFeedback result={orphanResult} />
          </div>
        </div>
      </div>
    )
  }

  function renderInspectorContent() {
    return (
      <div className="space-y-4">
        <div>
          <select
            className="h-9 w-full max-w-xs rounded-md border border-input bg-background px-3 text-sm"
            value={inspectSourceId ?? ''}
            onChange={(e) => {
              const id = e.target.value ? Number(e.target.value) : null
              if (id) inspectSource(id)
              else {
                setInspectSourceId(null)
                setSourceStats(null)
                setSourcePreview([])
              }
            }}
          >
            <option value="">{t('admin.chooseSource')}</option>
            {sources.map((s) => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
        </div>

        {inspectLoading && (
          <div className="space-y-3">
            <Skeleton className="h-32" />
            <Skeleton className="h-48" />
          </div>
        )}

        {!inspectLoading && sourceStats && (
          <>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
              <div>
                <p className="text-sm text-muted-foreground">{t('admin.articleCount')}</p>
                <p className="text-lg font-bold tabular-nums">{sourceStats.article_count}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">{t('admin.avgLength')}</p>
                <p className="text-lg font-bold tabular-nums">
                  {sourceStats.avg_content_length
                    ? `${Math.round(sourceStats.avg_content_length / 1000)}K`
                    : '—'}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">{t('admin.status')}</p>
                <Badge variant={sourceStats.is_active ? 'default' : 'secondary'}>
                  {sourceStats.is_active ? t('admin.active') : t('admin.inactive')}
                </Badge>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">{t('admin.earliest')}</p>
                <p className="text-sm">
                  {sourceStats.earliest_article
                    ? new Date(sourceStats.earliest_article).toLocaleDateString()
                    : '—'}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">{t('admin.latest')}</p>
                <p className="text-sm">
                  {sourceStats.latest_article
                    ? new Date(sourceStats.latest_article).toLocaleDateString()
                    : '—'}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">{t('admin.lastFetched')}</p>
                <p className="text-sm">
                  {sourceStats.last_fetched
                    ? new Date(sourceStats.last_fetched).toLocaleString()
                    : '—'}
                </p>
              </div>
            </div>

            {sourcePreview.length > 0 && (
              <div>
                <h3 className="mb-2 text-sm font-semibold">{t('admin.recentArticles')}</h3>
                <div className="divide-y rounded-md border">
                  {sourcePreview.map((item) => (
                    <div key={item.id} className="px-4 py-2">
                      <div className="flex items-start justify-between gap-2">
                        <p className="text-sm font-medium">{item.title}</p>
                        <span className="shrink-0 text-xs text-muted-foreground">
                          {new Date(item.published_at).toLocaleDateString()}
                        </span>
                      </div>
                      {item.snippet && (
                        <p className="mt-0.5 text-xs text-muted-foreground line-clamp-2">
                          {item.snippet}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {sourcePreview.length === 0 && sourceStats.article_count === 0 && (
              <p className="text-sm text-muted-foreground">{t('admin.noArticles')}</p>
            )}
          </>
        )}
      </div>
    )
  }

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  return (
    <div className="mx-auto space-y-6 px-4 py-6 md:px-6">
      {/* ==================== STAT CARDS ==================== */}
      <div className="grid grid-cols-3 gap-4">
        <StatCard label={t('admin.totalArticles')} value={stats?.total_articles ?? 0} />
        <StatCard label={t('admin.totalSources')} value={stats?.total_sources ?? 0} />
        <StatCard label={t('admin.totalIssues')} value={totalIssues} />
      </div>

      {/* ==================== ACCORDION-SIDEBAR ==================== */}
      <div className="flex gap-6">
        {/* Navigation stack */}
        <nav
          className={cn(
            'shrink-0 space-y-1.5 overflow-hidden',
            activeSection ? 'w-56' : 'w-full',
          )}
          style={{ transition: 'width 300ms cubic-bezier(0.4, 0, 0.2, 1)' }}
        >
          {sections.map((section) => {
            const isActive = activeSection === section.id
            return (
              <button
                key={section.id}
                type="button"
                onClick={() => toggleSection(section.id)}
                className={cn(
                  'group flex w-full items-center gap-3 rounded-lg border border-l-4 text-left',
                  section.accentColor,
                  activeSection ? 'px-3 py-2.5' : 'px-4 py-3.5',
                  isActive
                    ? 'bg-accent shadow-sm'
                    : 'hover:bg-accent/50',
                )}
                style={{ transition: 'padding 300ms cubic-bezier(0.4, 0, 0.2, 1), background-color 150ms' }}
              >
                <span className={cn(
                  'shrink-0 transition-colors',
                  isActive ? 'text-foreground' : 'text-muted-foreground',
                )}>
                  {section.icon}
                </span>
                <div className="min-w-0 flex-1">
                  <span className="block truncate text-sm font-medium">
                    {section.title}
                  </span>
                  {!activeSection && section.description && (
                    <span className="block truncate text-xs text-muted-foreground mt-0.5">
                      {section.description}
                    </span>
                  )}
                </div>
                {section.badge != null && section.badge > 0 && (
                  <Badge
                    variant={section.badgeVariant ?? 'secondary'}
                    className="shrink-0 text-xs"
                  >
                    {section.badge}
                  </Badge>
                )}
                {isActive && (
                  <ChevronRight className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
                )}
              </button>
            )
          })}
        </nav>

        {/* Content panel */}
        {activeSection && (
          <div className="min-w-0 flex-1 animate-in fade-in slide-in-from-left-3 duration-200">
            <Card>
              <CardHeader className="pb-4">
                <CardTitle className="flex items-center gap-2 text-base">
                  {sections.find((s) => s.id === activeSection)?.icon}
                  {sections.find((s) => s.id === activeSection)?.title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {activeSection === 'articles' && renderArticlesContent()}
                {activeSection === 'quality' && renderQualityContent()}
                {activeSection === 'actions' && renderActionsContent()}
                {activeSection === 'inspector' && renderInspectorContent()}
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}
