import type {
  FeatureFlags,
  NewsFilters,
  NewsItem,
  PaginatedNewsResponse,
  Source,
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

export async function fetchNewsContent(
  id: number,
): Promise<{ success: boolean; content?: string; message?: string }> {
  const res = await fetch(`/api/news/${id}/fetch-content`, { method: 'POST' })
  if (!res.ok) {
    throw new Error(`Failed to fetch content: ${res.status}`)
  }
  return res.json()
}
