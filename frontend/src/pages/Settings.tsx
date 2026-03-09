import { useEffect, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
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
  summary_max_words: number
  scheduler_enabled: boolean
  news_retention_days: number
}

type Theme = 'light' | 'dark' | 'system'

export default function Settings() {
  const queryClient = useQueryClient()
  const { theme, setTheme } = useTheme()
  const { t } = useTranslation()

  const [settings, setSettings] = useState<SettingsData>({
    ollama_endpoint: 'http://localhost:11434',
    ollama_model: 'deepseek-r1:7b',
    ai_enabled: true,
    summary_max_words: 200,
    scheduler_enabled: true,
    news_retention_days: 30,
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
      setError(t('settings.errorLoad'))
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
      alert(t('settings.successSave'))
    } catch {
      alert(t('settings.errorSave'))
    } finally {
      setSaving(false)
    }
  }

  const clearCache = () => {
    queryClient.clear()
    alert(t('settings.successClearCache'))
  }

  const themeOptions: { value: Theme; label: string }[] = [
    { value: 'light', label: t('settings.themeLight') },
    { value: 'dark', label: t('settings.themeDark') },
    { value: 'system', label: t('settings.themeSystem') },
  ]

  return (
    <div className="mx-auto max-w-4xl px-4 py-6 md:px-6">
      <div className="mb-6">
        <h1 className="font-serif text-3xl font-bold">{t('settings.title')}</h1>
        <p className="mt-1 text-muted-foreground">
          {t('settings.description')}
        </p>
      </div>

      {/* Theme Preferences */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>{t('settings.appearance')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <label className="text-sm font-medium">{t('settings.themeLabel')}</label>
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
              {t('settings.themeSystemHelp')}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* AI Configuration */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {t('settings.aiConfig')}
            {!loading && (
              <Badge variant={settings.ai_enabled ? 'default' : 'secondary'}>
                {settings.ai_enabled ? t('settings.aiActive') : t('settings.aiInactive')}
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
                {t('common.retry')}
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
                  {t('settings.aiEnable')}
                </label>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">{t('settings.ollamaEndpoint')}</label>
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
                  {t('settings.ollamaEndpointHelp')}
                </p>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">{t('settings.ollamaModel')}</label>
                <Input
                  value={settings.ollama_model}
                  onChange={(e) =>
                    setSettings({ ...settings, ollama_model: e.target.value })
                  }
                  placeholder="deepseek-r1:7b"
                />
                <p className="text-sm text-muted-foreground">
                  {t('settings.ollamaModelHelp')}
                </p>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">
                  {t('settings.summaryMaxWords')}
                </label>
                <Input
                  type="number"
                  min={50}
                  max={1000}
                  value={settings.summary_max_words}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      summary_max_words: Number(e.target.value) || 200,
                    })
                  }
                />
                <p className="text-sm text-muted-foreground">
                  {t('settings.summaryMaxWordsHelp')}
                </p>
              </div>

              <Button onClick={saveSettings} disabled={saving}>
                {saving ? t('settings.saving') : t('settings.saveSettings')}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Feed & Scheduler */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>{t('settings.feedUpdates')}</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-4">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : error ? null : (
            <div className="space-y-5">
              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  id="scheduler-enabled"
                  checked={settings.scheduler_enabled}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      scheduler_enabled: e.target.checked,
                    })
                  }
                  className="h-4 w-4 rounded border-input"
                />
                <label htmlFor="scheduler-enabled" className="text-sm font-medium">
                  {t('settings.schedulerEnabled')}
                </label>
              </div>
              <p className="text-sm text-muted-foreground">
                {t('settings.schedulerHelp')}
              </p>

              <Separator />

              <div className="space-y-2">
                <label className="text-sm font-medium">
                  {t('settings.newsRetention')}
                </label>
                <Input
                  type="number"
                  min={7}
                  max={365}
                  value={settings.news_retention_days}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      news_retention_days: Number(e.target.value) || 30,
                    })
                  }
                />
                <p className="text-sm text-muted-foreground">
                  {t('settings.newsRetentionHelp')}
                </p>
              </div>

              <Button onClick={saveSettings} disabled={saving}>
                {saving ? t('settings.saving') : t('settings.saveSettings')}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Cache Management */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>{t('settings.dataManagement')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">{t('settings.cacheLabel')}</p>
              <p className="text-sm text-muted-foreground">
                {t('settings.cacheHelp')}
              </p>
            </div>
            <Button variant="outline" onClick={clearCache}>
              {t('settings.clearCache')}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Help */}
      <Card>
        <CardHeader>
          <CardTitle>{t('settings.aiGuide')}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-3 text-sm text-muted-foreground">
            {t('settings.aiGuideIntro')}
          </p>
          <ol className="list-decimal space-y-1.5 pl-5 text-sm leading-relaxed">
            <li>
              {t('settings.aiGuideStep1')}{' '}
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
              {t('settings.aiGuideStep2')}{' '}
              <code className="rounded bg-muted px-1.5 py-0.5 text-xs">
                ollama pull deepseek-r1:7b
              </code>
            </li>
            <li>{t('settings.aiGuideStep3')}</li>
            <li>{t('settings.aiGuideStep4')}</li>
            <li>{t('settings.aiGuideStep5')}</li>
          </ol>
        </CardContent>
      </Card>
    </div>
  )
}
