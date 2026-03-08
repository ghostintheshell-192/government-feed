import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import type { NewsFilters, Source } from '@/lib/types'
import { FilterBar } from './filter-bar'

function makeSource(overrides: Partial<Source> = {}): Source {
  return {
    id: 1,
    name: 'Gazzetta Ufficiale',
    description: null,
    feed_url: 'https://example.com/feed',
    source_type: 'rss',
    category: null,
    update_frequency_minutes: 60,
    is_active: true,
    last_fetched: null,
    created_at: '2026-01-01T00:00:00',
    updated_at: '2026-01-01T00:00:00',
    ...overrides,
  }
}

const defaultProps = {
  filters: {} as NewsFilters,
  sources: [
    makeSource({ id: 1, name: 'Gazzetta Ufficiale' }),
    makeSource({ id: 2, name: 'MEF', is_active: false }),
    makeSource({ id: 3, name: 'MISE' }),
  ],
  recentSearches: [] as string[],
  onChange: vi.fn(),
  onSaveSearch: vi.fn(),
}

function renderBar(props: Partial<typeof defaultProps> = {}) {
  return render(<FilterBar {...defaultProps} {...props} />)
}

describe('FilterBar', () => {
  it('renders search input', () => {
    renderBar()
    expect(screen.getByPlaceholderText('Cerca nelle notizie...')).toBeInTheDocument()
  })

  it('renders source dropdown with only active sources', () => {
    renderBar()
    expect(screen.getByText('Tutte le fonti')).toBeInTheDocument()
    expect(screen.getByText('Gazzetta Ufficiale')).toBeInTheDocument()
    expect(screen.getByText('MISE')).toBeInTheDocument()
    // MEF is inactive, should not appear
    expect(screen.queryByText('MEF')).not.toBeInTheDocument()
  })

  it('renders date inputs', () => {
    renderBar()
    expect(screen.getByText('Da')).toBeInTheDocument()
    expect(screen.getByText('A')).toBeInTheDocument()
  })

  it('calls onChange with search value', async () => {
    const onChange = vi.fn()
    renderBar({ onChange })

    await userEvent.type(screen.getByPlaceholderText('Cerca nelle notizie...'), 't')

    expect(onChange).toHaveBeenCalled()
    const lastCall = onChange.mock.calls[onChange.mock.calls.length - 1][0]
    expect(typeof lastCall).toBe('function')
    // The updater receives prev state and adds the typed character
    const result = lastCall({ search: undefined })
    expect(result.search).toBe('t')
  })

  it('calls onChange when selecting a source', async () => {
    const onChange = vi.fn()
    renderBar({ onChange })

    await userEvent.selectOptions(
      screen.getByRole('combobox'),
      '1',
    )

    const lastCall = onChange.mock.calls[onChange.mock.calls.length - 1][0]
    expect(typeof lastCall).toBe('function')
    const result = lastCall({})
    expect(result.source_id).toEqual([1])
  })

  it('does not show clear/save buttons when no filters', () => {
    renderBar({ filters: {} })
    expect(screen.queryByText('Pulisci filtri')).not.toBeInTheDocument()
    expect(screen.queryByText('Salva ricerca')).not.toBeInTheDocument()
  })

  it('shows clear/save buttons when filters are active', () => {
    renderBar({ filters: { search: 'test' } })
    expect(screen.getByText('Pulisci filtri')).toBeInTheDocument()
    expect(screen.getByText('Salva ricerca')).toBeInTheDocument()
  })

  it('clears filters on button click', async () => {
    const onChange = vi.fn()
    renderBar({ filters: { search: 'test' }, onChange })

    await userEvent.click(screen.getByText('Pulisci filtri'))
    expect(onChange).toHaveBeenCalledWith({})
  })

  it('calls onSaveSearch on button click', async () => {
    const onSaveSearch = vi.fn()
    renderBar({ filters: { search: 'test' }, onSaveSearch })

    await userEvent.click(screen.getByText('Salva ricerca'))
    expect(onSaveSearch).toHaveBeenCalled()
  })

  it('shows recent searches dropdown on focus', async () => {
    renderBar({ recentSearches: ['previous query', 'old search'] })

    await userEvent.click(screen.getByPlaceholderText('Cerca nelle notizie...'))
    expect(screen.getByText('Ricerche recenti')).toBeInTheDocument()
    expect(screen.getByText('previous query')).toBeInTheDocument()
    expect(screen.getByText('old search')).toBeInTheDocument()
  })

  it('does not show recent searches when search has value', async () => {
    renderBar({
      filters: { search: 'current' },
      recentSearches: ['previous query'],
    })

    await userEvent.click(screen.getByPlaceholderText('Cerca nelle notizie...'))
    expect(screen.queryByText('Ricerche recenti')).not.toBeInTheDocument()
  })

  it('applies recent search on click', async () => {
    const onChange = vi.fn()
    renderBar({ recentSearches: ['old query'], onChange })

    await userEvent.click(screen.getByPlaceholderText('Cerca nelle notizie...'))
    // Use mouseDown since the component uses onMouseDown
    const recentItem = screen.getByText('old query')
    await userEvent.pointer({ target: recentItem, keys: '[MouseLeft]' })

    // Should have been called with functional updater
    const matchingCall = onChange.mock.calls.find((call) => {
      if (typeof call[0] === 'function') {
        const result = call[0]({})
        return result.search === 'old query'
      }
      return false
    })
    expect(matchingCall).toBeTruthy()
  })

  it('shows filters with source_id active', () => {
    renderBar({ filters: { source_id: [1] } })
    expect(screen.getByText('Pulisci filtri')).toBeInTheDocument()
  })

  it('shows filters with date_from active', () => {
    renderBar({ filters: { date_from: '2026-01-01T00:00:00' } })
    expect(screen.getByText('Pulisci filtri')).toBeInTheDocument()
  })
})
