# UI Preferences

**Status**: backlog
**Milestone**: M4a-Feed-Infrastructure
**Priority**: nice-to-have
**Depends on**: [frontend-base](../implemented/frontend-base.md)

## Summary

User interface customization including dark mode, language preference, TailwindCSS migration for consistent styling, and React Query integration for efficient data management.

## User Stories

- As a user, I want dark mode for comfortable reading at night
- As a user, I want to choose the interface language
- As a developer, I want a consistent styling system (TailwindCSS)

## Requirements

### Functional

- [ ] Dark mode toggle (system preference detection + manual override)
- [ ] Language preference (Italian/English initially)
- [ ] Theme persistence across sessions (localStorage)
- [ ] TailwindCSS migration from CSS modules
- [ ] React Query integration for data fetching, caching, and state management

### Non-Functional

- UX: Theme switch is instant (no flash of wrong theme)
- Consistency: All components follow design system
- Performance: React Query reduces unnecessary API calls

## Technical Notes

- TailwindCSS: utility-first CSS framework, replaces CSS modules
- React Query: handles data fetching, caching, background refetching
- Dark mode: CSS custom properties + Tailwind dark variant
- Language: i18n library (react-i18next or similar)
- Preferences stored in localStorage, synced to backend settings if multi-user

## Acceptance Criteria

- [ ] Dark mode works across all pages
- [ ] System color scheme is detected and respected
- [ ] Language can be switched without page reload
- [ ] TailwindCSS is integrated with consistent design
- [ ] React Query manages all API data fetching
