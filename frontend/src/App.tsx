import { BrowserRouter, Routes, Route, Link, Navigate } from 'react-router-dom'
import { ThemeToggle } from './components/theme-toggle'
import Sources from './pages/Sources'
import Feed from './pages/Feed'
import NewsDetail from './pages/NewsDetail'
import Settings from './pages/Settings'

function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen flex-col">
        <nav className="border-b bg-background px-4 py-3 shadow-sm md:px-6 md:py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="text-lg font-bold text-primary no-underline md:text-xl">
              Government Feed
            </Link>
            <div className="flex items-center gap-3 md:gap-6">
              <Link to="/" className="text-sm font-medium text-muted-foreground no-underline transition-colors hover:text-primary md:text-base">Dashboard</Link>
              <Link to="/sources" className="text-sm font-medium text-muted-foreground no-underline transition-colors hover:text-primary md:text-base">Sources</Link>
              <Link to="/settings" className="text-sm font-medium text-muted-foreground no-underline transition-colors hover:text-primary md:text-base">Impostazioni</Link>
              <ThemeToggle />
            </div>
          </div>
        </nav>

        <main className="flex-1 bg-muted/30">
          <Routes>
            <Route path="/" element={<Feed />} />
            <Route path="/feed" element={<Navigate to="/" replace />} />
            <Route path="/news/:id" element={<NewsDetail />} />
            <Route path="/sources" element={<Sources />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
