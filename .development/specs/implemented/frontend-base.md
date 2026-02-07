# Frontend Base

**Status**: implemented
**Milestone**: M1-MVP
**Priority**: should-have
**Depends on**: rest-api.md

## Summary

Basic React 18 + TypeScript frontend SPA with 4 pages (Home, Sources, Feed, Settings), built with Vite and CSS modules, providing a minimal but functional UI for the backend API.

## User Stories

- As a user, I want a web interface to browse news, manage sources, and configure settings
- As a user, I want to navigate between different sections of the application

## Requirements

### Functional

- [x] React 18 with TypeScript and strict mode
- [x] 4 pages: Home, Sources, Feed, Settings
- [x] Client-side routing between pages
- [x] API integration with backend endpoints
- [x] CSS modules for component styling
- [x] Vite as build tool with hot module replacement

### Non-Functional

- Build: Fast development builds via Vite HMR
- Type safety: TypeScript strict mode enabled
- Packaging: pnpm for dependency management

## Technical Notes

- Frontend structure: `frontend/src/`
  - `components/` — React components
  - `hooks/` — custom React hooks
  - `services/` — API client
  - `types/` — TypeScript type definitions
  - `App.tsx` — root component
- Build config: `frontend/vite.config.ts`
- Package manager: pnpm
- This is a basic scaffold; full frontend development is in M3-Frontend milestone
- See [dashboard-news-browsing](../backlog/dashboard-news-browsing.md), [search-discovery](../backlog/search-discovery.md), [news-detail-view](../backlog/news-detail-view.md) for planned frontend enhancements

## Acceptance Criteria

- [x] Application builds and runs with `pnpm dev`
- [x] All 4 pages are navigable
- [x] API calls to backend succeed (with CORS)
- [x] TypeScript compiles without errors
