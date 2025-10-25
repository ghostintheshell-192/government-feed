import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import Home from './pages/Home'
import Sources from './pages/Sources'
import Feed from './pages/Feed'
import Settings from './pages/Settings'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <nav className="navbar">
          <div className="nav-brand">
            <Link to="/">Government Feed</Link>
          </div>
          <div className="nav-links">
            <Link to="/">Home</Link>
            <Link to="/sources">Gestione Sources</Link>
            <Link to="/feed">Feed Reader</Link>
            <Link to="/settings">Impostazioni</Link>
          </div>
        </nav>

        <main className="main">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/sources" element={<Sources />} />
            <Route path="/feed" element={<Feed />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
