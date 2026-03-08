import { describe, expect, it } from 'vitest'
import { extractSnippet } from './search-snippet'

describe('extractSnippet', () => {
  const longText =
    'The Federal Reserve announced today that interest rates will remain unchanged. ' +
    'This decision was widely expected by market analysts who had been monitoring economic indicators. ' +
    'The central bank cited stable employment figures and moderate inflation as key factors in their decision. ' +
    'Markets responded positively to the announcement, with major indices rising slightly.'

  it('returns full text when shorter than maxLength', () => {
    expect(extractSnippet('Short text', undefined)).toBe('Short text')
  })

  it('truncates long text when no search term', () => {
    const result = extractSnippet(longText, undefined, 50)
    expect(result.length).toBeLessThanOrEqual(53) // 50 + '...'
    expect(result).toContain('...')
  })

  it('returns full text when search is empty string', () => {
    expect(extractSnippet('Short text', '')).toBe('Short text')
  })

  it('centers snippet around the match', () => {
    const result = extractSnippet(longText, 'inflation', 100)
    expect(result).toContain('inflation')
    expect(result.length).toBeLessThanOrEqual(106) // 100 + '...' x2
  })

  it('falls back to beginning when no match found', () => {
    const result = extractSnippet(longText, 'nonexistent', 50)
    expect(result).toContain('Federal Reserve')
    expect(result).toContain('...')
  })

  it('adds prefix when snippet starts mid-text', () => {
    const result = extractSnippet(longText, 'inflation', 80)
    expect(result.startsWith('...')).toBe(true)
  })

  it('no prefix when match is near beginning', () => {
    const result = extractSnippet(longText, 'Federal', 200)
    expect(result.startsWith('...')).toBe(false)
  })

  it('adds suffix when snippet ends before text end', () => {
    const result = extractSnippet(longText, 'Federal', 80)
    expect(result.endsWith('...')).toBe(true)
  })

  it('case-insensitive matching', () => {
    const result = extractSnippet(longText, 'INFLATION', 100)
    expect(result).toContain('inflation')
  })
})
