# Redis Caching

**Status**: planned
**Milestone**: M2-Production
**Priority**: should-have
**Depends on**: [rest-api](../implemented/rest-api.md)

## Summary

Redis-based caching layer for frequently accessed data with tiered TTL strategy: recent news (5min), source metadata (1h), AI summaries (permanent), reducing database load and improving response times.

## User Stories

- As a user, I want fast page loads when browsing recent news
- As a user, I want AI summaries to be instantly available after initial generation

## Requirements

### Functional

- [ ] Cache recent news queries with 5-minute TTL
- [ ] Cache source metadata with 1-hour TTL
- [ ] Cache AI summaries permanently (until content changes)
- [ ] Intelligent cache invalidation on data updates
- [ ] Cache bypass option for admin/debug operations
- [ ] Graceful fallback to database when Redis is unavailable

### Non-Functional

- Performance: Cached responses < 5ms vs 20-50ms from database
- Memory: Redis allocation ~512MB for single-user, ~2GB for small scale
- Availability: System fully functional without Redis (degraded performance)

## Technical Notes

- Redis 7+ for modern features
- Docker Compose service already configured (not yet active)
- Cache key patterns:
  - `news:recent:{limit}:{offset}` — paginated news list
  - `source:{id}` — source metadata
  - `summary:{news_id}` — AI summary text
- Invalidation triggers:
  - New news items → invalidate `news:recent:*`
  - Source update → invalidate `source:{id}`
  - New summary → set `summary:{news_id}`
- Consider using `redis-py` async client for consistency with FastAPI

## Open Questions

- Redis connection pool size for single vs multi-user scenarios
- Whether to cache full news items or just IDs (memory vs speed tradeoff)

## Acceptance Criteria

- [ ] Recent news list is served from cache when available
- [ ] Cache is invalidated correctly on data changes
- [ ] System works without Redis (database fallback)
- [ ] Response time improvement measurable (< 5ms cached vs 20-50ms uncached)
- [ ] Redis memory usage stays within allocated limits
