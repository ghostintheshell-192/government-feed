# Feed Registry

**Status**: backlog
**Milestone**: M4a-Feed-Infrastructure
**Priority**: should-have
**Depends on**: [source-management](../implemented/source-management.md)

## Summary

Community marketplace for discovering, contributing, and sharing institutional feed sources, evolving from a static GitHub JSON registry to a full backend-powered platform with accounts and ratings.

## User Stories

- As a new user, I want to discover institutional feeds without manually searching for URLs
- As a user, I want to contribute feeds I know about so others can benefit
- As a user, I want to see how popular and reliable a feed is before subscribing
- As a user, I want to import/export my feed configuration

## Requirements

### Functional

- [ ] Feed discovery: search by keyword, geography, category, language, institution type
- [ ] Feed contribution: submit new feed URL with title, description, tags, category
- [ ] Automatic feed validation (URL responds, content is valid RSS/Atom)
- [ ] Popularity metrics: follower count per feed
- [ ] "Feed simili consigliati" based on usage patterns
- [ ] "Feed non funzionante" community reporting
- [ ] One-click import of discovered feeds into personal sources

### Non-Functional

- Scale: Handle 1000+ feed entries efficiently
- Trust: Community validation improves feed quality over time

## Technical Notes

- **Phase 1**: GitHub repository with JSON file, static interface
  - JSON schema for feed entries (see vision.md for example)
  - Simple web interface to browse feeds
  - Contribution via pull requests
- **Phase 2**: Backend API + database for dynamic registry
  - REST API for CRUD operations on registry entries
  - Search and filter capabilities
  - Import/export API
- **Phase 3**: User accounts, ratings, moderation
  - User profiles for contributors
  - Rating system (1-5 stars)
  - Trending feeds based on recent subscriptions
  - Admin moderation tools
- Feed configuration JSON schema defined in vision.md

## Open Questions

- Self-hosted registry vs centralized community registry?
- Moderation model for contributed feeds
- How to handle feed URL changes or dead feeds

## Acceptance Criteria

- [ ] Users can discover feeds by keyword and category
- [ ] Users can contribute new feeds
- [ ] Feed URLs are automatically validated
- [ ] Feeds can be imported with one click
- [ ] Popularity/reliability metrics are visible
