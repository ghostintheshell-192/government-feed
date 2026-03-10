import { BrowserRouter, Routes, Route, Link, Navigate, useLocation, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ChevronRight } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { ThemeToggle } from './components/theme-toggle'
import { LanguageToggle } from './components/language-toggle'
import { fetchNewsById } from './lib/api'
import Admin from './pages/Admin'
import Sources from './pages/Sources'
import Feed from './pages/Feed'
import NewsDetail from './pages/NewsDetail'
import Settings from './pages/Settings'

function NavLink({ to, children }: { to: string; children: React.ReactNode }) {
  const { pathname } = useLocation()
  const isActive = to === '/' ? pathname === '/' : pathname.startsWith(to)

  return (
    <Link
      to={to}
      className={`text-sm font-medium no-underline transition-colors md:text-base ${
        isActive
          ? 'text-primary'
          : 'text-muted-foreground hover:text-primary'
      }`}
    >
      {children}
    </Link>
  )
}

function ArticleCrumb() {
  const { id } = useParams<{ id: string }>()
  const { data: item } = useQuery({
    queryKey: ['news-detail', Number(id)],
    queryFn: () => fetchNewsById(Number(id)),
    enabled: !!id,
  })

  if (!item) return null

  const truncated =
    item.title.length > 60 ? item.title.slice(0, 60) + '…' : item.title

  return (
    <>
      <ChevronRight className="h-3 w-3 shrink-0" />
      <span className="truncate">{truncated}</span>
    </>
  )
}

function Breadcrumb() {
  const { pathname } = useLocation()
  const { t } = useTranslation()

  const segments: { label: string; to?: string }[] = []

  if (pathname === '/') {
    segments.push({ label: t('breadcrumb.dashboard') })
  } else if (pathname.startsWith('/news/')) {
    segments.push({ label: t('breadcrumb.dashboard'), to: '/' })
  } else if (pathname === '/sources') {
    segments.push({ label: t('breadcrumb.sources') })
  } else if (pathname === '/admin') {
    segments.push({ label: t('breadcrumb.admin') })
  } else if (pathname === '/settings') {
    segments.push({ label: t('breadcrumb.settings') })
  }

  return (
    <div className="sticky top-0 z-10 border-b bg-background/80 backdrop-blur-sm">
      <div className={`mx-auto flex items-center gap-1.5 px-4 py-2 text-xs text-muted-foreground md:px-6 ${pathname === '/admin' ? '' : 'max-w-4xl'}`}>
        {segments.map((seg, i) => (
          <span key={i} className="flex items-center gap-1.5">
            {i > 0 && <ChevronRight className="h-3 w-3 shrink-0" />}
            {seg.to ? (
              <Link
                to={seg.to}
                className="no-underline transition-colors hover:text-primary"
              >
                {seg.label}
              </Link>
            ) : (
              <span>{seg.label}</span>
            )}
          </span>
        ))}
        {pathname.startsWith('/news/') && (
          <Routes>
            <Route path="/news/:id" element={<ArticleCrumb />} />
          </Routes>
        )}
      </div>
    </div>
  )
}

function AppLayout() {
  const { t } = useTranslation()

  return (
    <div className="flex min-h-screen flex-col">
      <nav className="border-b bg-background px-4 py-3 shadow-sm md:px-6 md:py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="font-serif text-xl font-bold tracking-tight text-primary no-underline md:text-2xl">
            {t('nav.brand')}
          </Link>
          <div className="flex items-center gap-3 md:gap-6">
            <NavLink to="/">{t('nav.dashboard')}</NavLink>
            <NavLink to="/sources">{t('nav.sources')}</NavLink>
            <NavLink to="/admin">{t('nav.admin')}</NavLink>
            <NavLink to="/settings">{t('nav.settings')}</NavLink>
            <LanguageToggle />
            <ThemeToggle />
          </div>
        </div>
      </nav>

      <Breadcrumb />

      <main className="flex-1 bg-muted/30">
        <Routes>
          <Route path="/" element={<Feed />} />
          <Route path="/feed" element={<Navigate to="/" replace />} />
          <Route path="/news/:id" element={<NewsDetail />} />
          <Route path="/sources" element={<Sources />} />
          <Route path="/admin" element={<Admin />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </main>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <AppLayout />
    </BrowserRouter>
  )
}

export default App
