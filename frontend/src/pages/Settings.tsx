import { useEffect, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'
import { useTheme } from '@/lib/theme-provider'

interface SettingsData {
  ollama_endpoint: string
  ollama_model: string
  ai_enabled: boolean
}

type Theme = 'light' | 'dark' | 'system'

export default function Settings() {
  const queryClient = useQueryClient()
  const { theme, setTheme } = useTheme()

  const [settings, setSettings] = useState<SettingsData>({
    ollama_endpoint: 'http://localhost:11434',
    ollama_model: 'deepseek-r1:7b',
    ai_enabled: true,
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('/api/settings')
      if (!res.ok) throw new Error(`Errore ${res.status}`)
      const data = await res.json()
      setSettings(data)
    } catch {
      setError('Impossibile caricare le impostazioni. Verifica che il backend sia attivo.')
    } finally {
      setLoading(false)
    }
  }

  const saveSettings = async () => {
    setSaving(true)
    try {
      const res = await fetch('/api/settings', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings),
      })
      if (!res.ok) throw new Error(`Errore ${res.status}`)
      alert('Impostazioni salvate!')
    } catch {
      alert('Errore nel salvataggio delle impostazioni.')
    } finally {
      setSaving(false)
    }
  }

  const clearCache = () => {
    queryClient.clear()
    alert('Cache dati svuotata. Le prossime pagine caricheranno dati freschi.')
  }

  const themeOptions: { value: Theme; label: string }[] = [
    { value: 'light', label: 'Chiaro' },
    { value: 'dark', label: 'Scuro' },
    { value: 'system', label: 'Sistema' },
  ]

  return (
    <div className="mx-auto max-w-3xl px-4 py-6 md:px-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Impostazioni</h1>
        <p className="mt-1 text-muted-foreground">
          Configura AI locale e altre preferenze
        </p>
      </div>

      {/* Theme Preferences */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Aspetto</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <label className="text-sm font-medium">Tema</label>
            <div className="flex gap-2">
              {themeOptions.map((opt) => (
                <Button
                  key={opt.value}
                  variant={theme === opt.value ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setTheme(opt.value)}
                >
                  {opt.label}
                </Button>
              ))}
            </div>
            <p className="text-sm text-muted-foreground">
              Seleziona &quot;Sistema&quot; per seguire le preferenze del tuo
              dispositivo.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* AI Configuration */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            Configurazione AI (Ollama)
            {!loading && (
              <Badge variant={settings.ai_enabled ? 'default' : 'secondary'}>
                {settings.ai_enabled ? 'Attiva' : 'Disattivata'}
              </Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-4">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-3/4" />
            </div>
          ) : error ? (
            <div className="py-8 text-center">
              <p className="text-destructive">{error}</p>
              <Button variant="outline" className="mt-4" onClick={loadSettings}>
                Riprova
              </Button>
            </div>
          ) : (
            <div className="space-y-5">
              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  id="ai-enabled"
                  checked={settings.ai_enabled}
                  onChange={(e) =>
                    setSettings({ ...settings, ai_enabled: e.target.checked })
                  }
                  className="h-4 w-4 rounded border-input"
                />
                <label htmlFor="ai-enabled" className="text-sm font-medium">
                  Abilita AI per riassunti automatici
                </label>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Endpoint Ollama</label>
                <Input
                  value={settings.ollama_endpoint}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      ollama_endpoint: e.target.value,
                    })
                  }
                  placeholder="http://localhost:11434"
                />
                <p className="text-sm text-muted-foreground">
                  Indirizzo del server Ollama locale. Predefinito:
                  http://localhost:11434
                </p>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Modello</label>
                <Input
                  value={settings.ollama_model}
                  onChange={(e) =>
                    setSettings({ ...settings, ollama_model: e.target.value })
                  }
                  placeholder="deepseek-r1:7b"
                />
                <p className="text-sm text-muted-foreground">
                  Nome del modello Ollama installato. Esempi: deepseek-r1:7b,
                  llama3.2, mistral
                </p>
              </div>

              <Button onClick={saveSettings} disabled={saving}>
                {saving ? 'Salvataggio...' : 'Salva Impostazioni'}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Cache Management */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Gestione Dati</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Cache dati</p>
              <p className="text-sm text-muted-foreground">
                Svuota la cache per forzare il ricaricamento di tutti i dati.
              </p>
            </div>
            <Button variant="outline" onClick={clearCache}>
              Svuota cache
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Help */}
      <Card>
        <CardHeader>
          <CardTitle>Guida AI</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-3 text-sm text-muted-foreground">
            Per utilizzare la funzionalità AI:
          </p>
          <ol className="list-decimal space-y-1.5 pl-5 text-sm leading-relaxed">
            <li>
              Installa Ollama dal sito ufficiale:{' '}
              <a
                href="https://ollama.ai"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary underline"
              >
                ollama.ai
              </a>
            </li>
            <li>
              Scarica un modello:{' '}
              <code className="rounded bg-muted px-1.5 py-0.5 text-xs">
                ollama pull deepseek-r1:7b
              </code>
            </li>
            <li>
              Avvia Ollama (di solito si avvia automaticamente
              all&apos;installazione)
            </li>
            <li>Configura endpoint e modello sopra</li>
            <li>
              Usa il bottone &quot;Riassumi&quot; nelle notizie per generare
              riassunti
            </li>
          </ol>
        </CardContent>
      </Card>
    </div>
  )
}
