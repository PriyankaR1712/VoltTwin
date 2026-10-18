
import { useState } from 'react'
import './App.css'

const API_BASE = 'http://127.0.0.1:8000'

type Scenario = {
  scenario: string
  initial_soh: number
  projected_soh: number
  projected_soh_percent: number
  additional_cycles: number
  recovery_assumption: number
  is_simulation: boolean
  difference_vs_baseline: number
}

type SimulationResult = {
  battery: {
    battery_id: string
    soh: number
    soh_percent: number
    cycle_count: number
  }
  predicted_soh: number
  predicted_soh_percent: number
  scenarios: Scenario[]
  recommendation: {
    recommended_scenario: string
    projected_soh: number
    status: string
    reason: string
    is_simulation_based: boolean
  }
  notice: string
}

function App() {
  const [batteryId, setBatteryId] = useState('XJTU-Battery-1')
  const [cycleCount, setCycleCount] = useState('389')
  const [additionalCycles, setAdditionalCycles] = useState('100')
  const [featuresText, setFeaturesText] = useState('')
  const [result, setResult] = useState<SimulationResult | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function runSimulation() {
    setError('')
    setResult(null)

    let features: number[]

    try {
      features = JSON.parse(featuresText)
      if (
        !Array.isArray(features) ||
        features.length !== 67 ||
        !features.every(
          (value) => typeof value === 'number' && Number.isFinite(value),
        )
      ) {
        setError('Please enter exactly 67 valid numeric feature values.')
        return
      }
    } catch {
      setError('Features must be a valid JSON array containing 67 numbers.')
      return
    }

    if (!batteryId.trim()) {
      setError('Please enter a battery ID.')
      return
    }

    const cycles = Number(cycleCount)
    const futureCycles = Number(additionalCycles)

    if (
      !Number.isInteger(cycles) ||
      cycles < 0 ||
      !Number.isInteger(futureCycles) ||
      futureCycles < 0 ||
      futureCycles > 100000
    ) {
      setError('Cycle counts must be valid non-negative whole numbers.')
      return
    }

    setLoading(true)

    try {
      const response = await fetch(`${API_BASE}/simulate-from-features`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          features,
          battery_id: batteryId.trim(),
          cycle_count: cycles,
          additional_cycles: futureCycles,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          typeof data.detail === 'string'
            ? data.detail
            : 'The API could not process this request.',
        )
      }

      setResult(data as SimulationResult)
    } catch (err) {
      setError(
        err instanceof Error
          ? `${err.message}. Check that the FastAPI backend is running.`
          : 'Unable to connect to the VoltTwin API.',
      )
    } finally {
      setLoading(false)
    }
  }

  const formatPercent = (value: number) => `${(value * 100).toFixed(2)}%`

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#" aria-label="VoltTwin home">
          <span className="brand-mark">V</span>
          <span>VoltTwin</span>
        </a>
        <span className="project-label">EV BATTERY INTELLIGENCE</span>
        <span className="connection"><span /> API-powered dashboard</span>
      </header>

      <section className="hero">
        <p className="eyebrow">PREDICT · SIMULATE · COMPARE</p>
        <h1>Understand your battery's<br /><span>next move.</span></h1>
        <p className="hero-copy">
          Predict battery State of Health, explore simulated future scenarios,
          and review a transparent maintenance recommendation.
        </p>
      </section>

      <section className="workspace">
        <div className="section-heading">
          <div>
            <p className="eyebrow">01 / INPUT</p>
            <h2>Battery configuration</h2>
          </div>
          <span className="step-tag">67 features required</span>
        </div>

        <div className="input-grid">
          <label>
            Battery ID
            <input
              value={batteryId}
              onChange={(event) => setBatteryId(event.target.value)}
              placeholder="e.g. XJTU-Battery-1"
            />
          </label>
          <label>
            Current cycle count
            <input
              type="number"
              min="0"
              step="1"
              value={cycleCount}
              onChange={(event) => setCycleCount(event.target.value)}
            />
          </label>
          <label>
            Additional cycles to simulate
            <input
              type="number"
              min="0"
              max="100000"
              step="1"
              value={additionalCycles}
              onChange={(event) => setAdditionalCycles(event.target.value)}
            />
          </label>
        </div>

        <label className="features-label">
          Handcrafted battery features
          <span>Paste the 67 numbers as a JSON array, in dataset column order.</span>
          <textarea
            rows={7}
            value={featuresText}
            onChange={(event) => setFeaturesText(event.target.value)}
            placeholder="[6.50844, 1.67940, 12.6000, ...]"
            spellCheck={false}
          />
        </label>

        <div className="form-footer">
          <p>Use a real dataset row. Do not include the label column.</p>
          <button onClick={runSimulation} disabled={loading}>
            {loading ? 'Running analysis…' : 'Run battery analysis'}
            {!loading && <span aria-hidden="true"> ↗</span>}
          </button>
        </div>

        {error && <div className="error-message" role="alert">{error}</div>}
      </section>

      {result && (
        <>
          <section className="results-section">
            <div className="section-heading">
              <div>
                <p className="eyebrow">02 / PREDICTION</p>
                <h2>Battery health estimate</h2>
              </div>
              <span className="status-pill">Prediction complete</span>
            </div>

            <div className="metric-grid">
              <article className="metric-card primary-metric">
                <p>Predicted State of Health</p>
                <strong>{result.predicted_soh_percent.toFixed(2)}%</strong>
                <div className="health-track">
                  <span style={{
                    width: `${Math.min(100, Math.max(0, result.predicted_soh_percent))}%`,
                  }} />
                </div>
                <small>Output from the trained CNN</small>
              </article>
              <article className="metric-card">
                <p>Battery identifier</p>
                <strong className="metric-text">{result.battery.battery_id}</strong>
                <small>Digital Twin instance</small>
              </article>
              <article className="metric-card">
                <p>Current cycle count</p>
                <strong>{result.battery.cycle_count.toLocaleString()}</strong>
                <small>Cycles supplied in the request</small>
              </article>
            </div>
          </section>

          <section className="results-section">
            <div className="section-heading">
              <div>
                <p className="eyebrow">03 / COUNTERFACTUALS</p>
                <h2>Compare future scenarios</h2>
              </div>
              <span className="step-tag">
                +{Number(additionalCycles).toLocaleString()} cycles
              </span>
            </div>

            <div className="scenario-grid">
              {result.scenarios.map((scenario) => (
                <article className="scenario-card" key={scenario.scenario}>
                  <p>{scenario.scenario}</p>
                  <strong>{scenario.projected_soh_percent.toFixed(2)}%</strong>
                  <div className="health-track">
                    <span style={{
                      width: `${Math.min(100, Math.max(0, scenario.projected_soh_percent))}%`,
                    }} />
                  </div>
                  <div className="scenario-detail">
                    <span>Change vs. baseline</span>
                    <b>
                      {scenario.difference_vs_baseline > 0 ? '+' : ''}
                      {(scenario.difference_vs_baseline * 100).toFixed(2)} pp
                    </b>
                  </div>
                  <div className="scenario-detail">
                    <span>Recovery assumption</span>
                    <b>{(scenario.recovery_assumption * 100).toFixed(2)} pp</b>
                  </div>
                </article>
              ))}
            </div>
            <p className="chart-caption">
              Projected SOH is calculated using the configured degradation and
              recovery assumptions; these maintenance effects are illustrative.
            </p>
          </section>

          <section className="recommendation-card">
            <p className="eyebrow">04 / MAINTENANCE AGENT</p>
            <h2>Current recommendation</h2>
            <div className="recommendation-main">
              <div>
                <span className="recommendation-label">Selected scenario</span>
                <strong>{result.recommendation.recommended_scenario}</strong>
              </div>
              <div className="recommendation-soh">
                <span className="recommendation-label">Projected SOH</span>
                <strong>{formatPercent(result.recommendation.projected_soh)}</strong>
              </div>
            </div>
            <p>{result.recommendation.reason}</p>
            <span className="status-pill">{result.recommendation.status.replaceAll('_', ' ')}</span>
          </section>

          <aside className="notice" role="note">
            <strong>Interpret results responsibly</strong>
            <p>{result.notice}</p>
            <p>
              The SOH value is an ML prediction. Future degradation and
              maintenance recovery values are simulation assumptions, not
              experimentally validated maintenance outcomes.
            </p>
          </aside>
        </>
      )}

      <footer className="footer">
        <span>VoltTwin</span>
        <span>Software-based EV battery digital twin</span>
      </footer>
    </main>
  )
}

export default App
