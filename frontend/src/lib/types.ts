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
  health_status: 'healthy' | 'degraded' | 'unhealthy' | 'dead'
  consecutive_failures: number
  last_health_check: string | null
  last_healthy_at: string | null
  created_at: string
  updated_at: string
}

export interface HealthCheckResult {
  source_id: number
  source_name: string
  previous_status: string
  new_status: string
  consecutive_failures: number
  error: string | null
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

// Catalog types

export interface CatalogSource {
  id: number
  name: string
  description: string | null
  feed_url: string
  source_type: string
  category: string | null
  geographic_level: string | null
  country_code: string | null
  region: string | null
  tags: string[]
  is_curated: boolean
  is_subscribed: boolean
}

export interface PaginatedCatalogResponse {
  items: CatalogSource[]
  pagination: PaginationMeta
}

export interface CatalogStats {
  total_sources: number
  by_geographic_level: Record<string, number>
  top_tags: [string, number][]
}

export interface CatalogFilters {
  search?: string
  geographic_level?: string
  tag?: string
}

// Admin types

export interface NewsPreview {
  id: number
  title: string
  published_at: string
  snippet: string | null
}

export interface SourceStats {
  source_id: number
  source_name: string
  article_count: number
  earliest_article: string | null
  latest_article: string | null
  avg_content_length: number | null
  last_fetched: string | null
  is_active: boolean
}

export interface CleanupResult {
  matched: number
  deleted: number
  dry_run: boolean
}

export interface ReimportResult {
  purged: number
  imported: number
}

export interface BulkFetchProgress {
  current: number
  total: number
  title: string
  status: 'fetched' | 'skipped' | 'failed'
}

export interface BulkFetchResult {
  total: number
  fetched: number
  skipped: number
  failed: number
}

export interface HtmlResidueFlag {
  id: number
  title: string
  field: string
}

export interface HtmlResidueResult {
  flagged: HtmlResidueFlag[]
  fixed: number
  dry_run: boolean
}

export interface PerSourceCount {
  source_id: number
  source_name: string
  article_count: number
}

export interface GlobalStats {
  total_articles: number
  total_sources: number
  per_source: PerSourceCount[]
}

export interface ContentLengthFlag {
  id: number
  title: string
  length: number
}

export interface DuplicateTitle {
  title: string
  source_id: number
  count: number
}

export interface EmptySource {
  id: number
  name: string
}

export interface QualityReport {
  total_articles: number
  total_sources: number
  short_content: ContentLengthFlag[]
  long_content: ContentLengthFlag[]
  html_residue: HtmlResidueFlag[]
  duplicate_titles: DuplicateTitle[]
  empty_sources: EmptySource[]
}
