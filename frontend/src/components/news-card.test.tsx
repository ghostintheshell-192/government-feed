import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import type { NewsItem } from '@/lib/types'
import { NewsCard } from './news-card'

vi.mock('@/lib/api', () => ({
  summarizeNews: vi.fn(),
}))

import { summarizeNews } from '@/lib/api'

function makeItem(overrides: Partial<NewsItem> = {}): NewsItem {
  return {
    id: 1,
    source_id: 10,
    external_id: null,
    title: 'Test News Title',
    content: null,
    summary: null,
    published_at: '2026-03-01T12:00:00',
    fetched_at: '2026-03-01T12:00:00',
    relevance_score: null,
    verification_status: 'unverified',
    ...overrides,
  }
}

const defaultProps = {
  item: makeItem(),
  sourceName: 'Test Source',
  isRead: false,
  aiEnabled: false,
  onRead: vi.fn(),
  onSummaryUpdate: vi.fn(),
}

function renderCard(props: Partial<typeof defaultProps> = {}) {
  return render(
    <MemoryRouter>
      <NewsCard {...defaultProps} {...props} />
    </MemoryRouter>,
  )
}

describe('NewsCard', () => {
  it('renders title and source', () => {
    renderCard()
    expect(screen.getByText('Test News Title')).toBeInTheDocument()
    expect(screen.getByText('Test Source')).toBeInTheDocument()
  })

  it('renders formatted date in Italian', () => {
    renderCard()
    expect(screen.getByText(/1 marzo 2026/)).toBeInTheDocument()
  })

  it('shows unread indicator when not read', () => {
    const { container } = renderCard({ isRead: false })
    expect(container.querySelector('.bg-blue-500')).toBeInTheDocument()
  })

  it('hides unread indicator when read', () => {
    const { container } = renderCard({ isRead: true })
    expect(container.querySelector('.bg-blue-500')).not.toBeInTheDocument()
  })

  it('calls onRead when clicking unread card', async () => {
    const onRead = vi.fn()
    renderCard({ onRead })

    await userEvent.click(screen.getByText('Test News Title').closest('[class*="card"]')!)
    expect(onRead).toHaveBeenCalledWith(1)
  })

  it('does not call onRead when card is already read', async () => {
    const onRead = vi.fn()
    renderCard({ isRead: true, onRead })

    await userEvent.click(screen.getByText('Test News Title').closest('[class*="card"]')!)
    expect(onRead).not.toHaveBeenCalled()
  })

  it('shows summary as preview when available', () => {
    renderCard({ item: makeItem({ summary: 'A brief summary' }) })
    expect(screen.getByText('A brief summary')).toBeInTheDocument()
  })

  it('shows content snippet as preview when no summary', () => {
    renderCard({ item: makeItem({ content: 'Some article content here for preview.' }) })
    expect(screen.getByText('Some article content here for preview.')).toBeInTheDocument()
  })

  it('strips HTML tags from content snippet', () => {
    renderCard({
      item: makeItem({ content: '<p>Paragraph with <strong>bold</strong> text.</p>' }),
    })
    expect(screen.getByText('Paragraph with bold text.')).toBeInTheDocument()
  })

  it('truncates long content with ellipsis', () => {
    const longContent = 'Word '.repeat(100)
    renderCard({ item: makeItem({ content: longContent }) })
    const preview = screen.getByText(/Word/)
    expect(preview.textContent).toContain('...')
  })

  it('shows "Leggi articolo" link to detail page', () => {
    renderCard()
    const link = screen.getByText('Leggi articolo')
    expect(link).toBeInTheDocument()
    expect(link.closest('a')).toHaveAttribute('href', '/news/1')
  })

  it('shows "Riassumi con AI" button when AI enabled and no summary', () => {
    renderCard({ aiEnabled: true })
    expect(screen.getByText('Riassumi con AI')).toBeInTheDocument()
  })

  it('hides "Riassumi con AI" when AI disabled', () => {
    renderCard({ aiEnabled: false })
    expect(screen.queryByText('Riassumi con AI')).not.toBeInTheDocument()
  })

  it('hides "Riassumi con AI" when summary already exists', () => {
    renderCard({
      aiEnabled: true,
      item: makeItem({ summary: 'Already summarized' }),
    })
    expect(screen.queryByText('Riassumi con AI')).not.toBeInTheDocument()
  })

  it('calls summarizeNews and updates on success', async () => {
    const onSummaryUpdate = vi.fn()
    vi.mocked(summarizeNews).mockResolvedValue({
      success: true,
      summary: 'AI generated summary',
    })

    renderCard({ aiEnabled: true, onSummaryUpdate })

    await userEvent.click(screen.getByText('Riassumi con AI'))

    expect(summarizeNews).toHaveBeenCalledWith(1)
    expect(onSummaryUpdate).toHaveBeenCalledWith(1, 'AI generated summary')
  })

  it('shows "Apri originale" when external_id exists', () => {
    renderCard({
      item: makeItem({ external_id: 'https://example.com/article' }),
    })
    expect(screen.getByText('Apri originale')).toBeInTheDocument()
  })

  it('hides "Apri originale" when no external_id', () => {
    renderCard({ item: makeItem({ external_id: null }) })
    expect(screen.queryByText('Apri originale')).not.toBeInTheDocument()
  })

  it('title links to detail page', () => {
    renderCard()
    const titleLink = screen.getByText('Test News Title').closest('a')
    expect(titleLink).toHaveAttribute('href', '/news/1')
  })
})
