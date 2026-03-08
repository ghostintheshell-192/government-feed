import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { highlightMatches } from './highlight'

describe('highlightMatches', () => {
  it('returns plain text when no search term', () => {
    expect(highlightMatches('Hello world', undefined)).toBe('Hello world')
  })

  it('returns plain text when search is empty', () => {
    expect(highlightMatches('Hello world', '')).toBe('Hello world')
  })

  it('returns plain text when search is whitespace', () => {
    expect(highlightMatches('Hello world', '   ')).toBe('Hello world')
  })

  it('returns plain text when no match found', () => {
    expect(highlightMatches('Hello world', 'xyz')).toBe('Hello world')
  })

  it('wraps matching text in mark tags', () => {
    const result = highlightMatches('Hello world', 'world')
    render(<>{result}</>)
    const mark = screen.getByText('world')
    expect(mark.tagName).toBe('MARK')
  })

  it('highlights case-insensitively', () => {
    const result = highlightMatches('Hello WORLD', 'world')
    render(<>{result}</>)
    const mark = screen.getByText('WORLD')
    expect(mark.tagName).toBe('MARK')
  })

  it('highlights multiple occurrences', () => {
    const result = highlightMatches('test one test two test', 'test')
    render(<>{result}</>)
    const marks = screen.getAllByText('test')
    expect(marks.length).toBe(3)
    marks.forEach((mark) => expect(mark.tagName).toBe('MARK'))
  })

  it('escapes regex special characters in search', () => {
    const result = highlightMatches('price is $100 (USD)', '$100')
    render(<>{result}</>)
    const mark = screen.getByText('$100')
    expect(mark.tagName).toBe('MARK')
  })
})
