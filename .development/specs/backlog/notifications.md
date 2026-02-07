# Notifications

**Status**: backlog
**Milestone**: M4-Advanced
**Priority**: nice-to-have
**Depends on**: [background-workers](../planned/background-workers.md), [relevance-scoring](relevance-scoring.md)

## Summary

Configurable notification system with multiple channels: email digest (daily/weekly), desktop push notifications, and webhooks for integration with external tools.

## User Stories

- As a user, I want email digests of important news on a regular schedule
- As a user, I want desktop push notifications for critical alerts
- As a user, I want to configure which topics and sources trigger notifications

## Requirements

### Functional

- [ ] Configurable alert rules (by source, category, keyword, relevance score)
- [ ] Email digest: daily and/or weekly summary of important news
- [ ] Desktop push notifications for high-priority items
- [ ] Webhook notifications to external services (Slack, Telegram, etc.)
- [ ] Notification preferences UI (channels, frequency, filters)
- [ ] Notification history (what was sent, when)

### Non-Functional

- Timeliness: Push notifications within 5 minutes of item detection
- Reliability: Email delivery with retry on failure
- Privacy: Notification content stays within user's control

## Technical Notes

- Email: SMTP integration (configurable server), or SendGrid/Mailgun API for cloud
- Push: Web Push API (requires HTTPS and service worker)
- Webhooks: HTTP POST with configurable payload format
- Digest generation: background job on schedule (daily at 8:00, weekly on Monday)
- Requires [background-workers](../planned/background-workers.md) for scheduling
- Alert rules stored in database, evaluated during feed processing

## Open Questions

- SMTP vs external email service?
- Push notification browser support requirements
- Maximum notification frequency (rate limiting)

## Acceptance Criteria

- [ ] Email digests are sent on configured schedule
- [ ] Push notifications work on desktop browsers
- [ ] Webhook notifications fire correctly
- [ ] Users can configure notification preferences
- [ ] Notification rules correctly filter relevant items
