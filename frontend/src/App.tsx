
import { useEffect, useState } from 'react'
import { getHealth } from './services/api'
import type { HealthResponse } from './types/api'
import './App.css'

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false

    async function checkBackend() {
      try {
        const data = await getHealth()

        if (!cancelled) {
          setHealth(data)
          setError(null)
        }
      } catch {
        if (!cancelled) {
          setError('Backend unavailable. Check the FastAPI server.')
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    void checkBackend()

    return () => {
      cancelled = true
    }
  }, [])

  const connected = health?.status === 'ok'

  return (
    <main className="dashboard">
      <header className="topbar">
        <a className="brand" href="/" aria-label="SprintFlow home">
          <span className="brand-icon">S</span>
          SprintFlow
        </a>

        <span className="environment">LOCAL DEVELOPMENT</span>
      </header>

      <section className="welcome">
        <p className="eyebrow">YOUR TEAM WORKSPACE</p>
        <h1>Make progress, together.</h1>
        <p className="subtitle">
          Plan projects, organize tasks, and turn ideas into action.
        </p>
      </section>

      <section className="overview">
        <div className="section-heading">
          <div>
            <h2>Workspace overview</h2>
            <p>Your project management workspace at a glance.</p>
          </div>
        </div>

        <div className="cards">
          <article className="card">
            <span className="card-icon purple">P</span>
            <p className="card-label">Projects</p>
            <h3>Coming next</h3>
            <p className="card-description">
              Organize your team's work.
            </p>
          </article>

          <article className="card">
            <span className="card-icon blue">T</span>
            <p className="card-label">Tasks</p>
            <h3>Coming next</h3>
            <p className="card-description">
              Track work and priorities.
            </p>
          </article>

          <article className="card">
            <span className="card-icon green">AI</span>
            <p className="card-label">AI assistant</p>
            <h3>Coming next</h3>
            <p className="card-description">
              Break large tasks into subtasks.
            </p>
          </article>
        </div>
      </section>

      <section className="connection">
        <div>
          <p className="card-label">Backend connection</p>
          <h2>
            {loading
              ? 'Checking connection...'
              : connected
                ? 'API connected'
                : 'Connection failed'}
          </h2>
          <p className="card-description">
            {loading
              ? 'Contacting the SprintFlow API.'
              : connected
                ? `${health.project} backend is responding successfully.`
                : error}
          </p>
        </div>

        <span
          className={`status ${
            loading ? 'pending' : connected ? 'online' : 'offline'
          }`}
          role="status"
        >
          <span className="status-dot" />
          {loading ? 'Checking' : connected ? 'Online' : 'Offline'}
        </span>
      </section>

      <footer>
        SprintFlow · Built for focused teamwork
      </footer>
    </main>
  )
}

export default App
