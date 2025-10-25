import { useEffect, useState } from 'react'
import './Feed.css'

interface NewsItem {
  id: number
  source_id: number
  title: string
  content: string | null
  summary: string | null
  published_at: string
  fetched_at: string
  relevance_score: number | null
}

export default function Feed() {
  const [news, setNews] = useState<NewsItem[]>([])
  const [loading, setLoading] = useState(true)
  const [summarizing, setSummarizing] = useState<number | null>(null)
  const [aiEnabled, setAiEnabled] = useState(true)

  useEffect(() => {
    loadNews()
    checkAiEnabled()
  }, [])

  const loadNews = async () => {
    setLoading(true)
    const res = await fetch('/api/news?limit=50')
    const data = await res.json()
    setNews(data)
    setLoading(false)
  }

  const checkAiEnabled = async () => {
    const res = await fetch('/api/settings/features')
    const data = await res.json()
    setAiEnabled(data.ai_enabled)
  }

  const summarizeNews = async (newsId: number) => {
    setSummarizing(newsId)
    const res = await fetch(`/api/news/${newsId}/summarize`, { method: 'POST' })
    const data = await res.json()

    if (data.success) {
      // Update news item with new summary
      setNews((prev) =>
        prev.map((item) =>
          item.id === newsId ? { ...item, summary: data.summary } : item
        )
      )
    } else {
      alert(data.message || 'Errore nella generazione del riassunto')
    }

    setSummarizing(null)
  }

  return (
    <div className="feed-page">
      <div className="page-header">
        <div>
          <h1>Feed Reader</h1>
          <p className="subtitle">Leggi le ultime notizie dai feed istituzionali</p>
        </div>
      </div>

      {loading ? (
        <div className="loading">Caricamento notizie...</div>
      ) : news.length === 0 ? (
        <div className="empty-state">
          <h3>Nessuna notizia disponibile</h3>
          <p>
            Non ci sono ancora notizie da visualizzare.
            <br />
            Vai su <a href="/sources">Gestione Sources</a> per aggiungere feed e poi usa
            il pulsante "Importa" per caricare le notizie.
          </p>
        </div>
      ) : (
        <>
          <div className="news-count">{news.length} notizie trovate</div>
          <div className="news-list">
            {news.map((item) => (
              <article key={item.id} className="news-card">
                <h2>{item.title}</h2>
                <div className="news-meta">
                  <span className="date">
                    {new Date(item.published_at).toLocaleDateString('it-IT', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })}
                  </span>
                  {aiEnabled && (
                    <button
                      className="btn btn-sm btn-ai"
                      onClick={() => summarizeNews(item.id)}
                      disabled={summarizing === item.id}
                    >
                      {summarizing === item.id ? '⏳ Generando...' : '🤖 Riassumi'}
                    </button>
                  )}
                </div>
                {item.summary && <p className="summary">{item.summary}</p>}
                {item.content && !item.summary && (
                  <p className="content">
                    {item.content.slice(0, 300)}
                    {item.content.length > 300 ? '...' : ''}
                  </p>
                )}
              </article>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
