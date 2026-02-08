import { BrowserRouter, Routes, Route, Link, Navigate } from 'react-router-dom'
import Sources from './pages/Sources'
import Feed from './pages/Feed'
import NewsDetail from './pages/NewsDetail'
import Settings from './pages/Settings'

function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen flex-col">
        <nav className="flex items-center justify-between border-b bg-white px-6 py-4 shadow-sm">
          <Link to="/" className="text-xl font-bold text-blue-600 no-underline">
            Government Feed
          </Link>
          <div className="flex gap-6">
            <Link to="/" className="font-medium text-gray-500 no-underline transition-colors hover:text-blue-600">Dashboard</Link>
            <Link to="/sources" className="font-medium text-gray-500 no-underline transition-colors hover:text-blue-600">Gestione Sources</Link>
            <Link to="/settings" className="font-medium text-gray-500 no-underline transition-colors hover:text-blue-600">Impostazioni</Link>
          </div>
        </nav>

        <main className="flex-1 bg-gray-50">
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
