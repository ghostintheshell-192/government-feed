---
type: bug
priority: medium
status: open
discovered: 2026-02-08
related: []
related_decision: null
report: null
---

# NewsCard: AI summary hidden when article content is expanded

## Problem

In the NewsCard component, when a user first generates an AI summary and then clicks "Mostra articolo" to view the full content, the summary disappears. The expanded content replaces the preview area where the summary was displayed.

## Analysis

The render logic in `news-card.tsx` is mutually exclusive:

```tsx
{!expanded && preview && (
  <p>{preview}</p>  // shows summary OR content slice
)}

{expanded && item.content && (
  <p>{item.content}</p>  // replaces everything above
)}
```

The `preview` variable prioritizes summary: `item.summary || item.content.slice(0, 200)`. But when `expanded` is `true`, the preview (including the summary) is hidden entirely.

## Possible Solutions

- **Option A**: Always show summary above content when both exist. Render summary in its own block (not inside the preview conditional), then show content below it when expanded. Simple and clear.
- **Option B**: Show summary as a highlighted card (similar to NewsDetail page style with blue background) above the expandable content area. More visually distinct but heavier.

## Recommended Approach

Option A — always render the summary independently from the expanded/collapsed state. Minimal change, fixes the bug cleanly.

## Notes

- The NewsDetail page already handles this correctly (summary and content are separate sections)
- Consider aligning the NewsCard and NewsDetail visual treatment of summaries for consistency

## Related Documentation

- **Code Locations**: `frontend/src/components/news-card.tsx` (lines ~78-120)
- **Related page**: `frontend/src/pages/NewsDetail.tsx` (summary section with blue card)
