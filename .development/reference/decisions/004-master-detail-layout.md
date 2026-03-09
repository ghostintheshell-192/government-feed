# ADR-004: Master-Detail Panel Layout for Dashboard

**Date**: 2026-03-08
**Status**: Proposed
**Impact**: significant

## Context

The current dashboard displays a list of news cards that link to a separate detail page for reading. This works but underutilizes screen space on desktop — the content area occupies less than half the available canvas. Users must navigate away from the list to read an article, losing context.

The news reader pattern (Feedly, Outlook, Apple Mail) suggests a master-detail layout where the article list and article content coexist side by side.

## Proposed Decision

Implement a responsive master-detail panel layout:

- **Desktop (≥1024px)**: Clicking an article opens a detail panel on the right (~60-65% width). The list narrows on the left (~35-40%), showing only titles and metadata (no preview text). A smooth slide transition (200-300ms) animates the panel opening.
- **Mobile (<1024px)**: Maintain current behavior — clicking navigates to a separate detail page. The list remains full-width with previews.

The detail page (`/news/:id`) continues to exist as a standalone route for direct links, bookmarks, and mobile navigation.

## Rationale

- **Space efficiency**: Desktop screens have enough width for both panels
- **Workflow continuity**: Users can scan the list while reading, reducing context switching
- **Triage-friendly**: Natural for a news aggregator where users scan many articles quickly
- **Progressive enhancement**: Mobile gets the simpler, proven UX; desktop gets the richer experience
- **No information loss**: The list panel still shows enough to identify articles (title, source, date, read status)

## Concerns

- **Visual complexity**: Two panels competing for attention — mitigated by clearly narrowing the list to titles only
- **Animation fatigue**: Transitions must be subtle and fast, not theatrical
- **Implementation scope**: Significant refactor of the Feed page layout and routing logic
- **State management**: Need to handle selected article state, keyboard navigation (up/down arrows), and URL synchronization

## Consequences

- **Positive**: Better use of screen real estate, faster article triage, more professional feel
- **Negative**: More complex layout code, responsive breakpoint logic, potential for split-attention
- **Trade-off**: Two rendering paths to maintain (panel vs. full page)
