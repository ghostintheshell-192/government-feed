import { useEffect, useState } from 'react'
import './Sources.css'

interface Source {
  id: number
  name: string
  description?: string
  feed_url: string
  source_type: string
  category?: string
  update_frequency_minutes: number
  is_active: boolean
  last_fetched?: string
}

interface SourceFormData {
  name: string
  description: string
  feed_url: string
  source_type: string
  category: string
  update_frequency_minutes: number
  is_active: boolean
}

export default function Sources() {
  const [sources, setSources] = useState<Source[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editMode, setEditMode] = useState(false)
  const [editId, setEditId] = useState<number | null>(null)
  const [processing, setProcessing] = useState<number | null>(null)
  const [formData, setFormData] = useState<SourceFormData>({
    name: '',
    description: '',
    feed_url: '',
    source_type: 'RSS',
    category: '',
    update_frequency_minutes: 60,
    is_active: true,
  })

  useEffect(() => {
    loadSources()
  }, [])

  const loadSources = async () => {
    setLoading(true)
    const res = await fetch('/api/sources')
    const data = await res.json()
    setSources(data)
    setLoading(false)
  }

  const openAddModal = () => {
    setEditMode(false)
    setEditId(null)
    setFormData({
      name: '',
      description: '',
      feed_url: '',
      source_type: 'RSS',
      category: '',
      update_frequency_minutes: 60,
      is_active: true,
    })
    setShowModal(true)
  }

  const openEditModal = (source: Source) => {
    setEditMode(true)
    setEditId(source.id)
    setFormData({
      name: source.name,
      description: source.description || '',
      feed_url: source.feed_url,
      source_type: source.source_type,
      category: source.category || '',
      update_frequency_minutes: source.update_frequency_minutes,
      is_active: source.is_active,
    })
    setShowModal(true)
  }

  const closeModal = () => {
    setShowModal(false)
    setFormData({
      name: '',
      description: '',
      feed_url: '',
      source_type: 'RSS',
      category: '',
      update_frequency_minutes: 60,
      is_active: true,
    })
  }

  const saveSource = async () => {
    if (!formData.name || !formData.feed_url) {
      alert('Nome e URL Feed sono obbligatori')
      return
    }

    const url = editMode ? `/api/sources/${editId}` : '/api/sources'
    const method = editMode ? 'PUT' : 'POST'

    await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
    })

    await loadSources()
    closeModal()
  }

  const deleteSource = async (id: number) => {
    if (!confirm('Eliminare questo feed?')) return
    await fetch(`/api/sources/${id}`, { method: 'DELETE' })
    await loadSources()
  }

  const toggleActive = async (source: Source) => {
    await fetch(`/api/sources/${source.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...source, is_active: !source.is_active }),
    })
    await loadSources()
  }

  const processFeed = async (id: number) => {
    setProcessing(id)
    const res = await fetch(`/api/sources/${id}/process`, { method: 'POST' })
    const data = await res.json()
    setProcessing(null)
    alert(data.message)
    await loadSources()
  }

  return (
    <div className="sources-page">
      <div className="page-header">
        <div>
          <h1>Gestione Sources</h1>
          <p className="subtitle">Configura e gestisci i feed istituzionali</p>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2>Feed Attivi</h2>
          <button className="btn btn-primary" onClick={openAddModal}>
            + Aggiungi Feed
          </button>
        </div>

        {loading ? (
          <div className="loading">Loading...</div>
        ) : sources.length === 0 ? (
          <div className="empty">
            Nessun feed configurato. Aggiungi il tuo primo feed per iniziare.
          </div>
        ) : (
          <table className="sources-table">
            <thead>
              <tr>
                <th>Nome</th>
                <th>URL</th>
                <th>Tipo</th>
                <th>Frequenza</th>
                <th>Ultima Fetch</th>
                <th>Stato</th>
                <th>Azioni</th>
              </tr>
            </thead>
            <tbody>
              {sources.map((source) => (
                <tr key={source.id}>
                  <td>
                    <strong>{source.name}</strong>
                    {source.description && (
                      <>
                        <br />
                        <small style={{ color: '#666' }}>{source.description}</small>
                      </>
                    )}
                  </td>
                  <td style={{ fontSize: '0.85rem', wordBreak: 'break-all' }}>
                    {source.feed_url}
                  </td>
                  <td>
                    <span className="badge">{source.source_type}</span>
                  </td>
                  <td>{source.update_frequency_minutes} min</td>
                  <td>
                    {source.last_fetched
                      ? new Date(source.last_fetched).toLocaleString('it-IT')
                      : 'Mai'}
                  </td>
                  <td>
                    <span className={`badge ${source.is_active ? 'active' : 'inactive'}`}>
                      {source.is_active ? 'Attivo' : 'Inattivo'}
                    </span>
                  </td>
                  <td>
                    <div className="actions">
                      {source.is_active && (
                        <button
                          className="btn btn-sm"
                          onClick={() => processFeed(source.id)}
                          disabled={processing === source.id}
                        >
                          {processing === source.id ? 'Importando...' : 'Importa'}
                        </button>
                      )}
                      <button
                        className="btn btn-sm"
                        onClick={() => openEditModal(source)}
                      >
                        Modifica
                      </button>
                      <button
                        className="btn btn-sm"
                        onClick={() => toggleActive(source)}
                      >
                        {source.is_active ? 'Disattiva' : 'Attiva'}
                      </button>
                      {!source.is_active && (
                        <button
                          className="btn btn-sm btn-danger"
                          onClick={() => deleteSource(source.id)}
                        >
                          Elimina
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showModal && (
        <div className="modal-backdrop" onClick={closeModal}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{editMode ? 'Modifica Feed' : 'Aggiungi Nuovo Feed'}</h3>
              <button className="close-btn" onClick={closeModal}>
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Nome *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Es: Governo Italiano"
                />
              </div>

              <div className="form-group">
                <label>Descrizione</label>
                <textarea
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                  placeholder="Descrizione opzionale"
                />
              </div>

              <div className="form-group">
                <label>URL Feed *</label>
                <input
                  type="url"
                  value={formData.feed_url}
                  onChange={(e) =>
                    setFormData({ ...formData, feed_url: e.target.value })
                  }
                  placeholder="https://example.com/feed.rss"
                />
              </div>

              <div className="form-group">
                <label>Tipo *</label>
                <select
                  value={formData.source_type}
                  onChange={(e) =>
                    setFormData({ ...formData, source_type: e.target.value })
                  }
                >
                  <option value="RSS">RSS</option>
                  <option value="Atom">Atom</option>
                  <option value="WebScraping">Web Scraping</option>
                  <option value="API">API</option>
                </select>
              </div>

              <div className="form-group">
                <label>Categoria</label>
                <input
                  type="text"
                  value={formData.category}
                  onChange={(e) =>
                    setFormData({ ...formData, category: e.target.value })
                  }
                  placeholder="Es: Governo Centrale"
                />
              </div>

              <div className="form-group">
                <label>Frequenza Aggiornamento (minuti) *</label>
                <input
                  type="number"
                  value={formData.update_frequency_minutes}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      update_frequency_minutes: parseInt(e.target.value),
                    })
                  }
                  min="1"
                />
              </div>

              {editMode && (
                <div className="form-group">
                  <label>
                    <input
                      type="checkbox"
                      checked={formData.is_active}
                      onChange={(e) =>
                        setFormData({ ...formData, is_active: e.target.checked })
                      }
                    />
                    Feed Attivo
                  </label>
                </div>
              )}
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={closeModal}>
                Annulla
              </button>
              <button className="btn btn-primary" onClick={saveSource}>
                {editMode ? 'Aggiorna' : 'Aggiungi'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
