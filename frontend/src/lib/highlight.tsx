import React from 'react'

/**
 * Split text by search term matches and wrap matches in <mark> tags.
 * Returns original text if no search term is provided.
 */
export function highlightMatches(
  text: string,
  search: string | undefined,
): React.ReactNode {
  if (!search || !search.trim()) return text

  const escaped = search.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const regex = new RegExp(`(${escaped})`, 'gi')
  const parts = text.split(regex)

  if (parts.length === 1) return text

  return parts.map((part, i) =>
    regex.test(part) ? (
      <mark key={i} className="rounded-sm bg-yellow-200 px-0.5 dark:bg-yellow-800 dark:text-yellow-100">
        {part}
      </mark>
    ) : (
      part
    ),
  )
}
