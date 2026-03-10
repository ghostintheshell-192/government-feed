import DOMPurify from 'dompurify'
import { type ReactNode } from 'react'

interface ArticleContentProps {
  content: string
  title?: string
  searchTerm?: string
  highlighter?: (text: string, term?: string) => ReactNode
  className?: string
}

const ALLOWED_TAGS = [
  'p',
  'h1',
  'h2',
  'h3',
  'h4',
  'h5',
  'h6',
  'ul',
  'ol',
  'li',
  'table',
  'thead',
  'tbody',
  'tfoot',
  'tr',
  'th',
  'td',
  'strong',
  'b',
  'em',
  'i',
  'blockquote',
  'a',
  'br',
  'sup',
  'sub',
  'caption',
  'img',
]

const ALLOWED_ATTR = ['href', 'src', 'alt']

/** Check if content contains HTML tags (from the new scraper). */
function isHtmlContent(content: string): boolean {
  return /<(?:p|h[1-6]|ul|ol|table|blockquote)\b/i.test(content)
}

/** Sanitize HTML content, preserving only safe semantic tags. */
function sanitizeHtml(html: string): string {
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS,
    ALLOWED_ATTR,
  })
}

/**
 * Remove an <h1> from HTML content if it substantially matches the article title.
 * Checks all <h1> tags, not just the first one (some sources prepend metadata h1s).
 * Uses normalized text comparison (lowercase, trimmed, punctuation-stripped).
 */
function removeLeadingDuplicateTitle(html: string, title: string): string {
  const normalize = (s: string) =>
    s.replace(/<[^>]+>/g, '').replace(/[\s\u00a0]+/g, ' ').replace(/[^\w\s]/g, '').trim().toLowerCase()

  const titleText = normalize(title)
  const h1Regex = /<h1\b[^>]*>[\s\S]*?<\/h1>/gi

  return html.replace(h1Regex, (match) => {
    const h1Text = normalize(match)
    if (h1Text.length > 10 && (titleText.includes(h1Text) || h1Text.includes(titleText))) {
      return ''
    }
    return match
  })
}

/**
 * Split a long plain-text block into paragraphs at sentence boundaries.
 * Targets ~3-4 sentences per paragraph for comfortable reading.
 */
function splitLongBlock(text: string): string[] {
  const sentences = text.split(/(?<=[.!?])\s+(?=[A-Z])/)
  if (sentences.length <= 3) return [text]

  const paragraphs: string[] = []
  let current: string[] = []

  for (const sentence of sentences) {
    current.push(sentence)
    if (current.length >= 3) {
      paragraphs.push(current.join(' '))
      current = []
    }
  }
  if (current.length > 0) {
    paragraphs.push(current.join(' '))
  }
  return paragraphs
}

/** Parse plain text into paragraphs (legacy content without HTML). */
function parsePlainText(content: string): string[] {
  const blocks = content
    .split(/\n\n+/)
    .map((p) => p.replace(/\n/g, ' ').trim())
    .filter((p) => p.length > 0)

  const result: string[] = []
  for (const block of blocks) {
    if (block.length > 600) {
      result.push(...splitLongBlock(block))
    } else {
      result.push(block)
    }
  }
  return result
}

/**
 * Renders article content with proper typography.
 *
 * Handles two formats:
 * 1. HTML content (new scraper) — sanitized and rendered with prose styling
 * 2. Plain text (legacy) — split into paragraphs with sentence-aware breaks
 */
export function ArticleContent({
  content,
  title,
  searchTerm,
  highlighter,
  className = '',
}: ArticleContentProps) {
  const proseClasses = `prose prose-neutral dark:prose-invert max-w-none prose-p:text-justify prose-p:leading-relaxed prose-headings:font-semibold prose-th:text-left prose-table:text-sm prose-td:py-1 prose-td:pr-4 prose-th:py-1 prose-th:pr-4 prose-img:mx-auto prose-img:rounded-md prose-img:bg-white prose-img:p-2 ${className}`

  if (isHtmlContent(content)) {
    let html = content
    if (title) {
      html = removeLeadingDuplicateTitle(html, title)
    }
    // Downgrade headings by 2 levels: the page already shows the article title,
    // so content headings should be less prominent (h1→h3, h2→h4, h3→h5, h4+→h6).
    html = html.replace(/<(\/?)h([1-6])\b/gi, (_, slash: string, level: string) => {
      const newLevel = Math.min(Number(level) + 2, 6)
      return `<${slash}h${newLevel}`
    })
    const clean = sanitizeHtml(html)
    return (
      <div
        className={proseClasses}
        dangerouslySetInnerHTML={{ __html: clean }}
      />
    )
  }

  // Legacy plain text content
  const paragraphs = parsePlainText(content)

  return (
    <div className={proseClasses}>
      {paragraphs.map((paragraph, index) => (
        <p key={index}>
          {highlighter ? highlighter(paragraph, searchTerm) : paragraph}
        </p>
      ))}
    </div>
  )
}
