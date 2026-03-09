/**
 * Extract a text snippet around the first occurrence of a search term.
 * Falls back to the beginning of the text if no match is found.
 */
export function extractSnippet(
  text: string,
  search: string | undefined,
  maxLength: number = 200,
): string {
  if (!search || !search.trim()) {
    return text.length > maxLength ? text.slice(0, maxLength) + '...' : text
  }

  const lowerText = text.toLowerCase()
  const lowerSearch = search.toLowerCase()
  const matchIndex = lowerText.indexOf(lowerSearch)

  if (matchIndex === -1) {
    return text.length > maxLength ? text.slice(0, maxLength) + '...' : text
  }

  // Center the snippet around the match
  const contextBefore = Math.floor((maxLength - search.length) / 2)
  let start = Math.max(0, matchIndex - contextBefore)
  let end = Math.min(text.length, start + maxLength)

  // Adjust start if we're near the end
  if (end === text.length && end - start < maxLength) {
    start = Math.max(0, end - maxLength)
  }

  // Snap to word boundaries
  if (start > 0) {
    const spaceAfter = text.indexOf(' ', start)
    if (spaceAfter !== -1 && spaceAfter < start + 20) {
      start = spaceAfter + 1
    }
  }
  if (end < text.length) {
    const spaceBefore = text.lastIndexOf(' ', end)
    if (spaceBefore > end - 20) {
      end = spaceBefore
    }
  }

  const snippet = text.slice(start, end)
  const prefix = start > 0 ? '...' : ''
  const suffix = end < text.length ? '...' : ''

  return prefix + snippet + suffix
}
