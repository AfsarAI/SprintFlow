import { useEffect, useState } from 'react'
import { AuthView } from './components/AuthView'
import { Workspace } from './components/Workspace'
import { getHealth, getMe, getStoredToken, removeStoredToken } from './services/api'
import type { HealthResponse, User } from './types'
import './App.css'

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false

    async function init() {
      // 1. Health check
      try {
        const data = await getHealth()
        if (!cancelled) {
          setHealth(data)
          setError(null)
        }
      } catch {
        if (!cancelled) {
          setError('Backend unavailable. Ensure the FastAPI server is running at port 8000.')
        }
      }

      // 2. Validate existing token session
      const token = getStoredToken()
      if (token) {
        try {
          const currentUser = await getMe()
          if (!cancelled) {
            setUser(currentUser)
          }
        } catch {
          removeStoredToken()
          if (!cancelled) {
            setUser(null)
          }
        }
      }

      if (!cancelled) {
        setLoading(false)
      }
    }

    void init()

    return () => {
      cancelled = true
    }
  }, [])

  const handleLogout = () => {
    removeStoredToken()
    setUser(null)
  }

  const handleAuthSuccess = (authenticatedUser: User) => {
    setUser(authenticatedUser)
  }

  return (
    <main className="dashboard">
      <header className="topbar">
        <a className="brand" href="/" aria-label="SprintFlow home">
          <span className="brand-icon">S</span>
          SprintFlow
        </a>

        <div className="topbar-right">
          <span className={`status-indicator ${health?.status === 'ok' ? 'online' : 'offline'}`}>
            <span className="dot"></span>
            {health?.status === 'ok' ? 'API Online' : 'API Offline'}
          </span>
          <span className="environment">LOCAL DEVELOPMENT</span>
        </div>
      </header>

      {error && (
        <div className="alert-error" style={{ marginTop: '16px' }} role="alert">
          {error}
        </div>
      )}

      {loading ? (
        <div className="loading-state" style={{ padding: '64px 0', textAlign: 'center' }}>
          Checking session & API health...
        </div>
      ) : user ? (
        <Workspace user={user} onLogout={handleLogout} />
      ) : (
        <AuthView onAuthSuccess={handleAuthSuccess} />
      )}

      <footer className="footer-status">
        <div className="footer-meta">
          <span>Backend: {health?.project || 'SprintFlow'}</span>
          <span>•</span>
          <span>Target: {import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}</span>
          <span>•</span>
          <span>JWT Auth: HS256 Protected</span>
        </div>
      </footer>
    </main>
  )
}

export default App
