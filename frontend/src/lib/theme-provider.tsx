import { createContext, useCallback, useContext, useEffect, useState } from 'react'

type Theme = 'light' | 'dark' | 'system'

export type Template =
  | 'financial-times'
  | 'hacker'
  | 'brutalist'
  | 'gazette'
  | 'minimal'

export const TEMPLATES: { value: Template; label: string }[] = [
  { value: 'financial-times', label: 'Financial Times' },
  { value: 'hacker', label: 'Hacker' },
  { value: 'brutalist', label: 'Brutalist' },
  { value: 'gazette', label: 'Gazette' },
  { value: 'minimal', label: 'Minimal' },
]

interface ThemeContextValue {
  theme: Theme
  resolvedTheme: 'light' | 'dark'
  setTheme: (theme: Theme) => void
  template: Template
  setTemplate: (template: Template) => void
}

const THEME_KEY = 'government-feed:theme'
const TEMPLATE_KEY = 'government-feed:template'

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined)

function getSystemTheme(): 'light' | 'dark' {
  if (typeof window === 'undefined') return 'light'
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function loadTheme(): Theme {
  try {
    const stored = localStorage.getItem(THEME_KEY)
    if (stored === 'light' || stored === 'dark' || stored === 'system') return stored
  } catch {
    // localStorage unavailable
  }
  return 'system'
}

function loadTemplate(): Template {
  try {
    const stored = localStorage.getItem(TEMPLATE_KEY)
    if (TEMPLATES.some((t) => t.value === stored)) return stored as Template
  } catch {
    // localStorage unavailable
  }
  return 'financial-times'
}

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<Theme>(loadTheme)
  const [systemTheme, setSystemTheme] = useState<'light' | 'dark'>(getSystemTheme)
  const [template, setTemplateState] = useState<Template>(loadTemplate)

  const resolvedTheme = theme === 'system' ? systemTheme : theme

  const setTheme = useCallback((newTheme: Theme) => {
    setThemeState(newTheme)
    try {
      localStorage.setItem(THEME_KEY, newTheme)
    } catch {
      // localStorage unavailable
    }
  }, [])

  const setTemplate = useCallback((newTemplate: Template) => {
    setTemplateState(newTemplate)
    try {
      localStorage.setItem(TEMPLATE_KEY, newTemplate)
    } catch {
      // localStorage unavailable
    }
  }, [])

  useEffect(() => {
    const mq = window.matchMedia('(prefers-color-scheme: dark)')
    const handler = (e: MediaQueryListEvent) => setSystemTheme(e.matches ? 'dark' : 'light')
    mq.addEventListener('change', handler)
    return () => mq.removeEventListener('change', handler)
  }, [])

  useEffect(() => {
    const root = document.documentElement
    root.classList.toggle('dark', resolvedTheme === 'dark')
    root.setAttribute('data-template', template)
  }, [resolvedTheme, template])

  return (
    <ThemeContext.Provider value={{ theme, resolvedTheme, setTheme, template, setTemplate }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) throw new Error('useTheme must be used within ThemeProvider')
  return context
}
