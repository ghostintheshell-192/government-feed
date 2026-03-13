import type {
  BulkFetchProgress,
  BulkFetchResult,
  CatalogFilters,
  CatalogStats,
  CleanupResult,
  FeatureFlags,
  GlobalStats,
  HealthCheckResult,
  HtmlResidueResult,
  NewsFilters,
  NewsItem,
  NewsPreview,
  PaginatedCatalogResponse,
  PaginatedNewsResponse,
  QualityReport,
  ReimportResult,
  Source,
  SourceStats,
  SummarizeResponse,
} from './types'

export async function fetchNews(
  limit: number,
  offset: number,
  filters: NewsFilters = {},
): Promise<PaginatedNewsResponse> {
  const params = new URLSearchParams()
  params.set('limit', String(limit))
  params.set('offset', String(offset))

  if (filters.search) {
    params.set('search', filters.search)
  }
  if (filters.date_from) {
    params.set('date_from', filters.date_from)
  }
  if (filters.date_to) {
    params.set('date_to', filters.date_to)
  }
  if (filters.source_id) {
    for (const id of filters.source_id) {
      params.append('source_id', String(id))
    }
  }

  const res = await fetch(`/api/news?${params.toString()}`)
  if (!res.ok) {
    throw new Error(`Failed to fetch news: ${res.status}`)
  }
  return res.json()
}

export async function fetchNewsById(id: number): Promise<NewsItem> {
  const res = await fetch(`/api/news/${id}`)
  if (!res.ok) {
    throw new Error(`Failed to fetch news item: ${res.status}`)
  }
  return res.json()
}

export async function fetchSources(): Promise<Source[]> {
  const res = await fetch('/api/sources')
  if (!res.ok) {
    throw new Error(`Failed to fetch sources: ${res.status}`)
  }
  return res.json()
}

export async function fetchFeatures(): Promise<FeatureFlags> {
  const res = await fetch('/api/settings/features')
  if (!res.ok) {
    throw new Error(`Failed to fetch features: ${res.status}`)
  }
  return res.json()
}

export async function summarizeNews(id: number): Promise<SummarizeResponse> {
  const res = await fetch(`/api/news/${id}/summarize`, { method: 'POST' })
  if (!res.ok) {
    throw new Error(`Failed to summarize news: ${res.status}`)
  }
  return res.json()
}

export interface DiscoveredFeed {
  url: string
  title: string
  feed_type: string
  site_url: string
  entry_count: number
}

export interface FeedDiscoveryResponse {
  feeds: DiscoveredFeed[]
  searched_sites: string[]
}

export async function discoverFeeds(
  query: string,
): Promise<FeedDiscoveryResponse> {
  const res = await fetch('/api/sources/discover', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  })
  if (!res.ok) {
    throw new Error(`Failed to discover feeds: ${res.status}`)
  }
  return res.json()
}

export async function fetchNewsContent(
  id: number,
  force: boolean = false,
): Promise<{ success: boolean; content?: string; message?: string }> {
  const params = force ? '?force=true' : ''
  const res = await fetch(`/api/news/${id}/fetch-content${params}`, {
    method: 'POST',
  })
  if (!res.ok) {
    throw new Error(`Failed to fetch content: ${res.status}`)
  }
  return res.json()
}

// ==================== HEALTH CHECK API ====================

export async function healthCheckSource(sourceId: number): Promise<HealthCheckResult> {
  const res = await fetch(`/api/sources/${sourceId}/health-check`, { method: 'POST' })
  if (!res.ok) throw new Error(`Failed to health check: ${res.status}`)
  return res.json()
}

export async function healthCheckAll(): Promise<HealthCheckResult[]> {
  const res = await fetch('/api/sources/health-check', { method: 'POST' })
  if (!res.ok) throw new Error(`Failed to bulk health check: ${res.status}`)
  return res.json()
}

// ==================== CATALOG API ====================

export async function fetchCatalog(
  limit: number,
  offset: number,
  filters: CatalogFilters = {},
): Promise<PaginatedCatalogResponse> {
  const params = new URLSearchParams()
  params.set('limit', String(limit))
  params.set('offset', String(offset))

  if (filters.search) params.set('search', filters.search)
  if (filters.geographic_level) params.set('geographic_level', filters.geographic_level)
  if (filters.tag) params.set('tag', filters.tag)

  const res = await fetch(`/api/catalog?${params.toString()}`)
  if (!res.ok) throw new Error(`Failed to fetch catalog: ${res.status}`)
  return res.json()
}

export async function fetchCatalogStats(): Promise<CatalogStats> {
  const res = await fetch('/api/catalog/stats')
  if (!res.ok) throw new Error(`Failed to fetch catalog stats: ${res.status}`)
  return res.json()
}

export async function subscribeToCatalog(sourceId: number): Promise<void> {
  const res = await fetch(`/api/catalog/${sourceId}/subscribe`, { method: 'POST' })
  if (res.status === 409) return // already subscribed
  if (!res.ok) throw new Error(`Failed to subscribe: ${res.status}`)
}

export async function unsubscribeFromCatalog(sourceId: number): Promise<void> {
  const res = await fetch(`/api/catalog/${sourceId}/subscribe`, { method: 'DELETE' })
  if (!res.ok) throw new Error(`Failed to unsubscribe: ${res.status}`)
}

// ==================== ADMIN API ====================

export async function fetchGlobalStats(): Promise<GlobalStats> {
  const res = await fetch('/api/admin/stats')
  if (!res.ok) throw new Error(`Failed to fetch stats: ${res.status}`)
  return res.json()
}

export async function fetchQualityReport(): Promise<QualityReport> {
  const res = await fetch('/api/admin/quality-report')
  if (!res.ok) throw new Error(`Failed to fetch quality report: ${res.status}`)
  return res.json()
}

export async function fetchSourceStats(sourceId: number): Promise<SourceStats> {
  const res = await fetch(`/api/admin/sources/${sourceId}/stats`)
  if (!res.ok) throw new Error(`Failed to fetch source stats: ${res.status}`)
  return res.json()
}

export async function fetchSourcePreview(sourceId: number, limit = 20): Promise<NewsPreview[]> {
  const res = await fetch(`/api/admin/sources/${sourceId}/preview?limit=${limit}`)
  if (!res.ok) throw new Error(`Failed to fetch preview: ${res.status}`)
  return res.json()
}

export async function purgeSource(sourceId: number): Promise<CleanupResult> {
  const res = await fetch(`/api/admin/sources/${sourceId}/purge`, { method: 'POST' })
  if (!res.ok) throw new Error(`Failed to purge source: ${res.status}`)
  return res.json()
}

export async function reimportSource(sourceId: number): Promise<ReimportResult> {
  const res = await fetch(`/api/admin/sources/${sourceId}/reimport`, { method: 'POST' })
  if (!res.ok) throw new Error(`Failed to reimport source: ${res.status}`)
  return res.json()
}

export async function bulkFetchContent(
  sourceId: number,
  force = false,
  onProgress?: (progress: BulkFetchProgress) => void,
): Promise<BulkFetchResult> {
  const res = await fetch(
    `/api/admin/sources/${sourceId}/fetch-content?force=${force}`,
    { method: 'POST' },
  )
  if (!res.ok) throw new Error(`Failed to bulk fetch content: ${res.status}`)

  // Read the NDJSON stream line by line
  const reader = res.body!.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let finalResult: BulkFetchResult | null = null

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    // Keep the last incomplete line in the buffer
    buffer = lines.pop() ?? ''

    for (const line of lines) {
      if (!line.trim()) continue
      const data = JSON.parse(line)
      if (data.done) {
        finalResult = data as BulkFetchResult
      } else if (onProgress) {
        onProgress(data as BulkFetchProgress)
      }
    }
  }

  // Process any remaining data in buffer
  if (buffer.trim()) {
    const data = JSON.parse(buffer)
    if (data.done) finalResult = data as BulkFetchResult
  }

  return finalResult ?? { total: 0, fetched: 0, skipped: 0, failed: 0 }
}

export async function cleanupByPattern(
  field: 'title' | 'content',
  pattern: string,
  sourceId?: number,
  dryRun = true,
): Promise<CleanupResult> {
  const res = await fetch('/api/admin/cleanup/by-pattern', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ field, pattern, source_id: sourceId, dry_run: dryRun }),
  })
  if (!res.ok) throw new Error(`Failed to cleanup by pattern: ${res.status}`)
  return res.json()
}

export async function cleanupHtmlResidue(dryRun = true): Promise<HtmlResidueResult> {
  const res = await fetch(`/api/admin/cleanup/html-residue?dry_run=${dryRun}`, { method: 'POST' })
  if (!res.ok) throw new Error(`Failed to cleanup HTML: ${res.status}`)
  return res.json()
}

export async function cleanupOrphans(): Promise<CleanupResult> {
  const res = await fetch('/api/admin/cleanup/orphans', { method: 'POST' })
  if (!res.ok) throw new Error(`Failed to cleanup orphans: ${res.status}`)
  return res.json()
}
