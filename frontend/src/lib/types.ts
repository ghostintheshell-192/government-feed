export interface NewsItem {
  id: number
  source_id: number
  external_id: string | null
  title: string
  content: string | null
  summary: string | null
  published_at: string
  fetched_at: string
  relevance_score: number | null
  verification_status: string
}

export interface Source {
  id: number
  name: string
  description: string | null
  feed_url: string
  source_type: string
  category: string | null
  update_frequency_minutes: number
  is_active: boolean
  last_fetched: string | null
  created_at: string
  updated_at: string
}

export interface PaginationMeta {
  total: number
  limit: number
  offset: number
  has_more: boolean
}

export interface PaginatedNewsResponse {
  items: NewsItem[]
  pagination: PaginationMeta
}

export interface FeatureFlags {
  ai_enabled: boolean
  verification_enabled: boolean
  blockchain_enabled: boolean
}

export interface SummarizeResponse {
  success: boolean
  summary: string
  message?: string
}

export interface NewsFilters {
  source_id?: number[]
  search?: string
  date_from?: string
  date_to?: string
}
