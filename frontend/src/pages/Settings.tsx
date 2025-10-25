import { useEffect, useState } from 'react'
import './Settings.css'

interface SettingsData {
  ollama_endpoint: string
  ollama_model: string
  ai_enabled: boolean
}

export default function Settings() {
  const [settings, setSettings] = useState<SettingsData>({
    ollama_endpoint: 'http://localhost:11434',
    ollama_model: 'deepseek-r1:7b',
    ai_enabled: true,
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    const res = await fetch('/api/settings')
    const data = await res.json()
    setSettings(data)
    setLoading(false)
  }

  const saveSettings = async () => {
    setSaving(true)
    await fetch('/api/settings', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings),
    })
    setSaving(false)
    alert('Impostazioni salvate!')
  }

  if (loading) return <div className="loading">Caricamento...</div>

  return (
    <div className="settings-page">
      <div className="page-header">
        <h1>Impostazioni</h1>
        <p className="subtitle">Configura AI locale e altre preferenze</p>
      </div>

      <div className="card">
        <div className="card-header">
          <h2>Configurazione AI (Ollama)</h2>
        </div>

        <div className="card-body">
          <div className="form-group">
            <label>
              <input
                type="checkbox"
                checked={settings.ai_enabled}
                onChange={(e) =>
                  setSettings({ ...settings, ai_enabled: e.target.checked })
                }
              />
              Abilita AI per riassunti automatici
            </label>
          </div>

          <div className="form-group">
            <label>Endpoint Ollama</label>
            <input
              type="text"
              value={settings.ollama_endpoint}
              onChange={(e) =>
                setSettings({ ...settings, ollama_endpoint: e.target.value })
              }
              placeholder="http://localhost:11434"
            />
            <small>
              Indirizzo del server Ollama locale. Predefinito: http://localhost:11434
            </small>
          </div>

          <div className="form-group">
            <label>Modello</label>
            <input
              type="text"
              value={settings.ollama_model}
              onChange={(e) =>
                setSettings({ ...settings, ollama_model: e.target.value })
              }
              placeholder="deepseek-r1:7b"
            />
            <small>
              Nome del modello Ollama installato. Esempi: deepseek-r1:7b, llama3.2,
              mistral
            </small>
          </div>

          <button
            className="btn btn-primary"
            onClick={saveSettings}
            disabled={saving}
          >
            {saving ? 'Salvataggio...' : 'Salva Impostazioni'}
          </button>
        </div>
      </div>

      <div className="card" style={{ marginTop: '2rem' }}>
        <div className="card-header">
          <h2>Note</h2>
        </div>
        <div className="card-body">
          <p style={{ marginBottom: '1rem' }}>
            Per utilizzare la funzionalità AI:
          </p>
          <ol style={{ paddingLeft: '1.5rem', lineHeight: '1.8' }}>
            <li>
              Installa Ollama dal sito ufficiale:{' '}
              <a
                href="https://ollama.ai"
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: '#1976d2' }}
              >
                ollama.ai
              </a>
            </li>
            <li>Scarica un modello: ollama pull deepseek-r1:7b</li>
            <li>
              Avvia Ollama (di solito si avvia automaticamente all'installazione)
            </li>
            <li>Configura endpoint e modello sopra</li>
            <li>
              Usa il bottone "Riassumi" nelle notizie per generare riassunti automatici
            </li>
          </ol>
        </div>
      </div>
    </div>
  )
}
