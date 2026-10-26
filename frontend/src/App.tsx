
import { useState } from 'react'
import './App.css'
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  ReferenceLine,
  Cell,
} from 'recharts'

const API_BASE = 'http://127.0.0.1:8000'
const SAMPLE_FEATURES_URL = '/sample_request.json'

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

type DegradationResult = {
  observation_count: number
  window_size_used: number
  latest_observed_soh: number
  trend_per_sample: number
  trend_percentage_points_per_sample: number
  trend_r_squared: number | null
  future_samples: number
  projected_soh: number
  projected_soh_percent: number
  is_historical_estimate: boolean
  is_future_forecast: boolean
  forecast_type: string
  notice: string
}

type HistoricalAnalysisResult = {
  dataset_file: string
  sheet_count: number
  analysis_type: string
  sheets: Record<
    string,
    {
      observation_count: number
      first_observed_soh: number
      last_observed_soh: number
      net_change_percentage_points: number
      linear_trend_percentage_points_per_sample: number
      recent_trend_percentage_points_per_sample: number
      linear_trend_r_squared: number
      trend_unit: string
      is_historical_analysis: boolean
      is_future_forecast: boolean
    }
  >
}

type ReplayObservation = {
  observation_index: number
  predicted_soh: number
  predicted_soh_percent: number
  actual_soh: number
  actual_soh_percent: number
  absolute_error: number
  twin_state: {
    battery_id: string
    soh: number
    soh_percent: number
    cycle_count: number
  }
}

type ReplayResult = {
  battery_id: string
  sheet_name: string
  observation_count: number
  mae: number
  mae_percentage_points: number
  rmse: number
  rmse_percentage_points: number
  
  rul_estimate: {
    current_soh: number
    current_soh_percent: number
    eol_threshold: number
    eol_threshold_percent: number
    rul_observations: number | null
    status: string
    trend_per_sample: number
    trend_r_squared: number | null
    unit: string
    is_physically_validated: boolean
    method: string
  }

  evaluation_type: string
  observation_order_is_verified_physical_cycle_order: boolean
  observations: ReplayObservation[]
  final_twin_state: {
    battery_id: string
    soh: number
    soh_percent: number
    cycle_count: number
  }
}

type AdaptiveMaintenanceResult = {
  hybrid_projection: {
    battery_id: string
    initial_soh: number
    projected_soh: number
    projected_soh_percent: number
    future_samples: number
    baseline_degradation_per_sample: number
    trend_per_sample: number
    trend_based_degradation_per_sample: number
    trend_weight: number
    trend_r_squared: number | null
    effective_trend_weight: number
    hybrid_degradation_per_sample: number
    model_type: string
    is_simulation: boolean
    is_physically_validated: boolean
  } | null
  controller_type: string
  maintenance_effects_validated: boolean
  battery: {
    battery_id: string
    soh: number
    soh_percent: number
    cycle_count: number
  }
  replay: ReplayResult
  degradation_trend: {
    observation_count: number
    window_size_used: number
    latest_observed_soh: number
    trend_per_sample: number
    trend_percentage_points_per_sample: number
    trend_r_squared: number | null
    is_historical_estimate: boolean
    is_future_forecast: boolean
  }
  scenarios: Scenario[]
  recommendation: {
    recommended_scenario: string
    projected_soh: number
    status: string
    reason: string
    current_soh: number
    trend_per_sample: number
    minimum_acceptable_soh: number
    is_simulation_based: boolean
    is_rule_based: boolean
    recommended_action: string
    action_steps: string[]
    required_evidence: string[]
    urgency: string
    decision_factors: {
      current_soh_below_threshold: boolean
      trend_is_declining: boolean
      trend_indicates_rapid_decline: boolean
      baseline_meets_threshold: boolean
      acceptable_scenario_count: number
    }
    available_action_categories: string[]
    is_adaptive_policy: boolean
    maintenance_effects_validated: boolean
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
  
  const [replaySheet, setReplaySheet] = useState('Sheet1')
  const [replayBatteryId, setReplayBatteryId] = useState('XJTU-Battery-1')
  const [replayResult, setReplayResult] = useState<ReplayResult | null>(null)
  const [replayError, setReplayError] = useState('')
  const [replayLoading, setReplayLoading] = useState(false)
  const [adaptiveResult, setAdaptiveResult] = useState<AdaptiveMaintenanceResult | null>(null)
  const [adaptiveError, setAdaptiveError] = useState('')
  const [adaptiveLoading, setAdaptiveLoading] = useState(false)
  const [thermalAlert, setThermalAlert] = useState(false)
  const [bmsFaultCodes, setBmsFaultCodes] = useState('')
  const [cellVoltageImbalance, setCellVoltageImbalance] = useState(false)
  const [chargingAnomaly, setChargingAnomaly] = useState(false)
  const [confirmedFault, setConfirmedFault] = useState(false)
  const [loading, setLoading] = useState(false)
  
  const [observedSohText, setObservedSohText] = useState('')
  const [futureSamples, setFutureSamples] = useState('25')
  const [windowSize, setWindowSize] = useState('25')
  const [degradationResult, setDegradationResult] =
    useState<DegradationResult | null>(null)
  const [historicalResult, setHistoricalResult] =
    useState<HistoricalAnalysisResult | null>(null)
  const [degradationError, setDegradationError] = useState('')
  const [degradationLoading, setDegradationLoading] = useState(false)

async function loadSampleBattery() {
  setError('')

  try {
    const response = await fetch(SAMPLE_FEATURES_URL)

    if (!response.ok) {
      throw new Error('Could not load the sample battery file.')
    }

    const sample = await response.json()

    if (!Array.isArray(sample.features) || sample.features.length !== 67) {
      throw new Error('The sample file must contain exactly 67 features.')
    }

    setFeaturesText(JSON.stringify(sample.features, null, 2))
    setBatteryId('XJTU-Battery-1')
    setCycleCount('389')
    setAdditionalCycles('100')
    setResult(null)
  } catch (err) {
    setError(
      err instanceof Error
        ? err.message
        : 'Unable to load the sample battery.',
    )
  }
}


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

  
async function runDegradationAnalysis() {
  setDegradationError('')
  setDegradationResult(null)

  let observedSoh: number[]

  try {
    observedSoh = JSON.parse(observedSohText)

    if (
      !Array.isArray(observedSoh) ||
      observedSoh.length < 3 ||
      !observedSoh.every(
        (value) =>
          typeof value === 'number' &&
          Number.isFinite(value) &&
          value >= 0 &&
          value <= 1,
      )
    ) {
      setDegradationError(
        'Enter at least 3 valid SOH values between 0 and 1 as a JSON array.',
      )
      return
    }
  } catch {
    setDegradationError(
      'SOH history must be a valid JSON array, such as [0.95, 0.94, 0.93].',
    )
    return
  }

  const future = Number(futureSamples)
  const window = Number(windowSize)

  if (
    !Number.isInteger(future) ||
    future < 0 ||
    future > 10000 ||
    !Number.isInteger(window) ||
    window < 3 ||
    window > 1000
  ) {
    setDegradationError(
      'Future samples must be 0–10000, and window size must be 3–1000.',
    )
    return
  }

  setDegradationLoading(true)

  try {
    const response = await fetch(`${API_BASE}/estimate-degradation`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        observed_soh: observedSoh,
        future_samples: future,
        window_size: window,
      }),
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(
        typeof data.detail === 'string'
          ? data.detail
          : 'The degradation API could not process this request.',
      )
    }

    setDegradationResult(data as DegradationResult)
  } catch (err) {
    setDegradationError(
      err instanceof Error
        ? `${err.message} Check that the FastAPI backend is running.`
        : 'Unable to connect to the degradation API.',
    )
  } finally {
    setDegradationLoading(false)
  }
}

async function loadHistoricalAnalysis() {
  setDegradationError('')
  setHistoricalResult(null)
  setDegradationLoading(true)

  try {
    const response = await fetch(`${API_BASE}/historical-analysis`)
    const data = await response.json()

    if (!response.ok) {
      throw new Error(
        typeof data.detail === 'string'
          ? data.detail
          : 'The historical-analysis API could not process this request.',
      )
    }

    setHistoricalResult(data as HistoricalAnalysisResult)
  } catch (err) {
    setDegradationError(
      err instanceof Error
        ? `${err.message} Check that the FastAPI backend is running.`
        : 'Unable to load historical analysis.',
    )
  } finally {
    setDegradationLoading(false)
  }
}

async function runSequentialReplay() {
  setReplayError('')
  setReplayResult(null)

  if (!replayBatteryId.trim()) {
    setReplayError('Please enter a battery ID.')
    return
  }

  setReplayLoading(true)

  try {
    const response = await fetch(`${API_BASE}/replay-battery`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sheet_name: replaySheet,
        battery_id: replayBatteryId.trim(),
      }),
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(
        typeof data.detail === 'string'
          ? data.detail
          : 'The replay API could not process this request.',
      )
    }

    setReplayResult(data as ReplayResult)
  } catch (err) {
    setReplayError(
      err instanceof Error
        ? `${err.message} Check that the FastAPI backend is running.`
        : 'Unable to connect to the VoltTwin replay API.',
    )
  } finally {
    setReplayLoading(false)
  }
}
async function runAdaptiveMaintenance() {
  setAdaptiveError('')
  setAdaptiveResult(null)

  if (!replayBatteryId.trim()) {
    setAdaptiveError('Please enter a battery ID.')
    return
  }

  setAdaptiveLoading(true)

  try {
    const response = await fetch(`${API_BASE}/adaptive-maintenance`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sheet_name: replaySheet,
        battery_id: replayBatteryId.trim(),
        diagnostic_evidence: {
          thermal_alert: thermalAlert,
          bms_fault_codes: bmsFaultCodes
            .split(',')
            .map((code) => code.trim())
            .filter(Boolean),
          cell_voltage_imbalance: cellVoltageImbalance,
          charging_anomaly: chargingAnomaly,
          confirmed_fault: confirmedFault,
        },
      }),
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(
        typeof data.detail === 'string'
          ? data.detail
          : 'The adaptive-maintenance API could not process this request.',
      )
    }

    setAdaptiveResult(data as AdaptiveMaintenanceResult)
  } catch (err) {
    setAdaptiveError(
      err instanceof Error
        ? `${err.message} Check that the FastAPI backend is running.`
        : 'Unable to connect to the adaptive-maintenance API.',
    )
  } finally {
    setAdaptiveLoading(false)
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
              onChange={(event) => {
                setBatteryId(event.target.value)
                setResult(null)
              }}
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
              onChange={(event) => {
                setCycleCount(event.target.value)
                setResult(null)
              }}
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
              onChange={(event) => {
                setAdditionalCycles(event.target.value)
                setResult(null)
              }}
            />
          </label>
        </div>

        <label className="features-label">
          Handcrafted battery features
          <span>Paste the 67 numbers as a JSON array, in dataset column order.</span>
          <textarea
            rows={7}
            value={featuresText}
            onChange={(event) => {
              setFeaturesText(event.target.value)
              setResult(null)
            }}
            placeholder="[6.50844, 1.67940, 12.6000, ...]"
            spellCheck={false}
          />
        </label>

        
        <div className="form-footer">
          <p>Use a real dataset row. Do not include the label column.</p>
          <div className="form-actions">
            <button
              type="button"
              className="secondary-button"
              onClick={loadSampleBattery}
              disabled={loading}
            >
              Load sample battery
            </button>
            <button onClick={runSimulation} disabled={loading}>
              {loading ? 'Running analysis…' : 'Run battery analysis'}
              {!loading && <span aria-hidden="true"> ↗</span>}
            </button>
          </div>
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

      <section className="workspace">
        <div className="section-heading">
          <div>
            <p className="eyebrow">05 / DEGRADATION ANALYSIS</p>
            <h2>Historical trend &amp; SOH projection</h2>
          </div>
          <span className="step-tag">Experimental forecast</span>
        </div>

        <label className="features-label">
          Historical SOH observations
          <span>
            Enter a JSON array of SOH fractions between 0 and 1, ordered
            from oldest to newest. Example: [0.95, 0.94, 0.93]
          </span>
          <textarea
            rows={5}
            value={observedSohText}
            onChange={(event) => setObservedSohText(event.target.value)}
            placeholder="[0.95, 0.94, 0.93, 0.92]"
            spellCheck={false}
          />
        </label>

        <div className="input-grid degradation-inputs">
          <label>
            Future samples
            <input
              type="number"
              min="0"
              max="10000"
              step="1"
              value={futureSamples}
              onChange={(event) => setFutureSamples(event.target.value)}
            />
          </label>

          <label>
            Recent trend window
            <input
              type="number"
              min="3"
              max="1000"
              step="1"
              value={windowSize}
              onChange={(event) => setWindowSize(event.target.value)}
            />
          </label>

          <div className="degradation-actions">
            <button
              type="button"
              onClick={runDegradationAnalysis}
              disabled={degradationLoading}
            >
              {degradationLoading ? 'Analyzing…' : 'Estimate degradation'}
            </button>
          </div>
        </div>

        <div className="form-footer">
          <p>Sample index is not a verified physical cycle count.</p>
          <button
            type="button"
            className="secondary-button"
            onClick={loadHistoricalAnalysis}
            disabled={degradationLoading}
          >
            Load XJTU historical analysis
          </button>
        </div>

        {degradationError && (
          <div className="error-message" role="alert">
            {degradationError}
          </div>
        )}

        {degradationResult && (
          <div className="degradation-results">
            <div className="metric-grid">
              <article className="metric-card primary-metric">
                <p>Latest observed SOH</p>
                <strong>
                  {(degradationResult.latest_observed_soh * 100).toFixed(2)}%
                </strong>
                <small>
                  {degradationResult.observation_count} observations supplied
                </small>
              </article>

              <article className="metric-card">
                <p>Recent trend</p>
                <strong>
                  {degradationResult.trend_percentage_points_per_sample.toFixed(4)}
                </strong>
                <small>Percentage points per sample</small>
              </article>

              <article className="metric-card">
                <p>Experimental projected SOH</p>
                <strong>{degradationResult.projected_soh_percent.toFixed(2)}%</strong>
                <small>
                  After {degradationResult.future_samples} future samples
                </small>
              </article>
            </div>

            <p className="chart-caption">
              Trend R²: {degradationResult.trend_r_squared === null
                ? 'Unavailable'
                : degradationResult.trend_r_squared.toFixed(4)}
              {' · '}Window used: {degradationResult.window_size_used}
            </p>

            <aside className="notice" role="note">
              <strong>Experimental projection</strong>
              <p>{degradationResult.notice}</p>
            </aside>
          </div>
        )}

        {historicalResult && (
          <div className="degradation-results">
            <h3>
              XJTU batch-1 observed trends ({historicalResult.sheet_count} sheets)
            </h3>

            <div className="historical-table-wrapper">
              <table className="historical-table">
                <thead>
                  <tr>
                    <th>Battery sheet</th>
                    <th>Observations</th>
                    <th>First SOH</th>
                    <th>Last SOH</th>
                    <th>Net change</th>
                    <th>Recent trend (pp/sample)</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(historicalResult.sheets).map(([name, sheet]) => (
                    <tr key={name}>
                      <td>{name}</td>
                      <td>{sheet.observation_count}</td>
                      <td>{(sheet.first_observed_soh * 100).toFixed(2)}%</td>
                      <td>{(sheet.last_observed_soh * 100).toFixed(2)}%</td>
                      <td>
                        {sheet.net_change_percentage_points.toFixed(2)} pp
                      </td>
                      <td>
                        {sheet.recent_trend_percentage_points_per_sample.toFixed(4)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <p className="chart-caption">
              These values describe observed historical data. They are not
              future forecasts or verified physical-cycle degradation rates.
            </p>
          </div>
        )}
      </section>
      

<section className="workspace">
  <div className="section-heading">
    <div>
      <p className="eyebrow">06 / SEQUENTIAL REPLAY</p>
      <h2>Replay battery history</h2>
    </div>
    <span className="step-tag">XJTU dataset</span>
  </div>

  <p className="chart-caption">
    Run the trained CNN against a battery's recorded observations,
    compare predicted and actual SOH, and inspect the final Digital Twin
    state. Observation order is not verified physical cycle order.
  </p>

  <div className="input-grid">
    <label>
      Battery dataset sheet
      <select
        value={replaySheet}
        onChange={(event) => {
          setReplaySheet(event.target.value)
          setReplayResult(null)
          setAdaptiveResult(null)
          setReplayError('')
          setAdaptiveError('')
        }}
      >
        {Array.from({ length: 8 }, (_, index) => `Sheet${index + 1}`).map(
          (sheet) => (
            <option key={sheet} value={sheet}>
              {sheet}
            </option>
          ),
        )}
      </select>
    </label>

    <label>
      Battery ID
      <input
        value={replayBatteryId}
        onChange={(event) => {
          setReplayBatteryId(event.target.value)
          setReplayResult(null)
          setAdaptiveResult(null)
          setReplayError('')
          setAdaptiveError('')
        }}
        placeholder="e.g. XJTU-Battery-1"
      />
    </label>
  </div>

  <div className="form-footer">
    <p>Predictions are evaluated against capacity-derived SOH labels.</p>
    <button
      type="button"
      onClick={runSequentialReplay}
      disabled={replayLoading}
    >
      {replayLoading ? 'Replaying observations…' : 'Run sequential replay'}
    </button>
  </div>

  {replayError && (
    <div className="error-message" role="alert">
      {replayError}
    </div>
  )}

  {replayResult && (
    <div className="degradation-results">
      <div className="metric-grid">
        <article className="metric-card primary-metric">
          <p>Observations processed</p>
          <strong>{replayResult.observation_count}</strong>
          <small>{replayResult.sheet_name}</small>
        </article>

        <article className="metric-card">
          <p>Mean absolute error</p>
          <strong>{replayResult.mae_percentage_points.toFixed(4)}</strong>
          <small>SOH percentage points</small>
        </article>

        <article className="metric-card">
          <p>Root mean squared error</p>
          <strong>{replayResult.rmse_percentage_points.toFixed(4)}</strong>
          <small>SOH percentage points</small>
        </article>
        
        <article className="metric-card primary-metric">
          <p>Estimated Remaining Useful Life</p>
          <strong>
            {replayResult.rul_estimate.rul_observations === null
              ? 'Unavailable'
              : replayResult.rul_estimate.rul_observations}
          </strong>
          <small>
            {replayResult.rul_estimate.status.replaceAll('_', ' ')}
            {' · '}
            {replayResult.rul_estimate.unit}
          </small>
          <small>
            EOL threshold: {replayResult.rul_estimate.eol_threshold_percent.toFixed(1)}% SOH
          </small>
        </article>

      </div>
      
      <h3>Remaining Useful Life & EOL Threshold</h3>
      <p className="chart-caption">
        Current SOH compared with the 80% reference threshold.
        RUL is expressed in observations, not verified physical cycles.
      </p>

      <div style={{ width: '100%', height: 300 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={[
              {
                name: 'Current SOH',
                value: replayResult.rul_estimate.current_soh_percent,
              },
              {
                name: 'EOL threshold',
                value: replayResult.rul_estimate.eol_threshold_percent,
              },
            ]}
            margin={{ top: 25, right: 20, left: 0, bottom: 10 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis
              domain={[
                (min: number) => Math.max(0, Math.floor(min - 5)),
                (max: number) => Math.min(100, Math.ceil(max + 5)),
              ]}
              tickFormatter={(value) => `${value}%`}
            />
            <Tooltip
              formatter={(value) =>
                typeof value === 'number'
                  ? `${value.toFixed(2)}%`
                  : value
              }
            />
            
            <Bar
              dataKey="value"
              name="SOH"
              label={{
                position: 'top',
                formatter: (value) =>
                  typeof value === 'number'
                    ? `${value.toFixed(2)}%`
                    : '',
              }}
            >
              {[
                replayResult.rul_estimate.current_soh_percent,
                replayResult.rul_estimate.eol_threshold_percent,
              ].map((_, index) => (
                <Cell
                  key={index}
                  fill={
                    index === 0 &&
                    replayResult.rul_estimate.current_soh_percent <=
                      replayResult.rul_estimate.eol_threshold_percent
                      ? '#dc2626'
                      : '#64748b'
                  }
                />
              ))}
            </Bar>

          </BarChart>
        </ResponsiveContainer>
      </div>

      <p className="chart-caption">
        RUL status: {replayResult.rul_estimate.status.replaceAll('_', ' ')}.
        This estimate is experimental and is not physically validated.
      </p>

      <p className="chart-caption">
        RUL is an experimental estimate in observations, not verified
        remaining battery cycles. The 80% end-of-life threshold is a
        configurable project assumption. This estimate is not physically
        validated.
      </p>
      
      <h3>Actual vs Predicted SOH</h3>
      <p className="chart-caption">
        CNN predictions compared with capacity-derived SOH labels.
      </p>

      <div style={{ width: '100%', height: 320 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={replayResult.observations}
            margin={{ top: 10, right: 20, left: 0, bottom: 10 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="observation_index"
              tick={{ fontSize: 12 }}
              label={{
                value: 'Observation index',
                position: 'insideBottom',
                offset: -5,
              }}
            />
            <YAxis
              domain={[0, 100]}
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => `${value}%`}
            />
            <Tooltip
              formatter={(value) =>
                typeof value === 'number'
                  ? `${value.toFixed(2)}%`
                  : value
              }
              labelFormatter={(label) => `Observation ${label}`}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="actual_soh_percent"
              name="Actual SOH"
              stroke="#16a34a"
              dot={false}
              strokeWidth={2}
            />
            <Line
              type="monotone"
              dataKey="predicted_soh_percent"
              name="Predicted SOH"
              stroke="#2563eb"
              dot={false}
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <h3>Observation results</h3>
      <div className="historical-table-wrapper">
        <table className="historical-table">
          <thead>
            <tr>
              <th>Index</th>
              <th>Predicted SOH</th>
              <th>Actual SOH</th>
              <th>Absolute error</th>
            </tr>
          </thead>
          <tbody>
            {replayResult.observations
              .filter(
                (_, index) =>
                  index < 5 ||
                  index >= replayResult.observations.length - 5,
              )
              .map((observation) => (
                <tr key={observation.observation_index}>
                  <td>{observation.observation_index}</td>
                  <td>{observation.predicted_soh_percent.toFixed(2)}%</td>
                  <td>{observation.actual_soh_percent.toFixed(2)}%</td>
                  <td>{(observation.absolute_error * 100).toFixed(4)} pp</td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>

      <p className="chart-caption">
        Showing the first and last five observations. Metrics use all
        observations in the selected sheet.
      </p>

      
      <aside className="notice" role="note">
        <strong>Final Digital Twin state</strong>

        <p>
          Battery: {replayResult.final_twin_state.battery_id}
          {' · '}
          Observed SOH:{' '}
          {replayResult.final_twin_state.soh_percent.toFixed(2)}%
        </p>

        <p>
          Observations processed: {replayResult.observation_count}
        </p>

        <p>
          Physical cycle count: Unverified / unavailable
        </p>

        <p>
          The twin's SOH is updated using observed historical data.
          The observation count represents the number of records replayed,
          not verified physical battery cycles. This is a historical
          replay, not a live battery stream.
        </p>
      </aside>

    </div>
  )}
</section>

<section className="workspace">
  <div className="section-heading">
    <div>
      <span className="eyebrow">07 / ADAPTIVE MAINTENANCE</span>
      <h2>Integrated adaptive maintenance</h2>
      <p>
        Replay battery history, compare maintenance scenarios, and receive
        a condition-aware recommendation.
      </p>
    </div>
  </div>
  <div className="diagnostic-inputs">
    <h3>Diagnostic evidence</h3>
    <p className="chart-caption">
      Enter only evidence you have actually observed or confirmed.
      These inputs are not automatically detected by the dataset.
    </p>

    <label>
      <input
        type="checkbox"
        checked={thermalAlert}
        onChange={(event) => setThermalAlert(event.target.checked)}
      />
      Thermal alert reported
    </label>

    <label>
      <input
        type="checkbox"
        checked={cellVoltageImbalance}
        onChange={(event) =>
          setCellVoltageImbalance(event.target.checked)
        }
      />
      Cell voltage imbalance reported
    </label>

    <label>
      <input
        type="checkbox"
        checked={chargingAnomaly}
        onChange={(event) => setChargingAnomaly(event.target.checked)}
      />
      Charging anomaly reported
    </label>

    <label>
      <input
        type="checkbox"
        checked={confirmedFault}
        onChange={(event) => setConfirmedFault(event.target.checked)}
      />
      Fault confirmed by diagnostic evidence
    </label>

    <label>
      BMS fault codes
      <span>Enter codes separated by commas, if available.</span>
      <input
        type="text"
        value={bmsFaultCodes}
        onChange={(event) => setBmsFaultCodes(event.target.value)}
        placeholder="e.g. BMS_01, BMS_02"
      />
    </label>
  </div>
  <div className="form-footer">
    <button
      className="primary-button"
      onClick={runAdaptiveMaintenance}
      disabled={adaptiveLoading}
    >
      {adaptiveLoading ? 'Analyzing battery...' : 'Run Adaptive Maintenance'}
    </button>
  </div>

  {adaptiveError && (
    <p className="error-message">{adaptiveError}</p>
  )}

  {adaptiveResult && (
    <>
      <div className="metric-grid">
        <div className="metric-card">
          <span>Observations</span>
          <strong>{adaptiveResult.replay.observation_count}</strong>
        </div>

        <div className="metric-card">
          <span>Current observed SOH</span>
          <strong>
            {adaptiveResult.battery.soh_percent.toFixed(2)}%
          </strong>
        </div>

        <div className="metric-card">
          <span>Replay MAE</span>
          <strong>
            {adaptiveResult.replay.mae_percentage_points.toFixed(2)} pp
          </strong>
        </div>

        <div className="metric-card">
          <span>Recent degradation trend</span>
          <strong>
            {adaptiveResult.degradation_trend
              .trend_percentage_points_per_sample.toFixed(4)} pp/sample
          </strong>
        </div>
      </div>
      <h3>Counterfactual Maintenance Comparison</h3>
      <p className="chart-caption">
        Comparison of projected SOH under different simulated maintenance scenarios.
      </p>

      <div style={{ width: '100%', height: 320 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={adaptiveResult.scenarios}
            margin={{ top: 10, right: 20, left: 0, bottom: 20 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="scenario"
              tick={{ fontSize: 11 }}
              interval={0}
            />
            <YAxis
              domain={[0, 100]}
              tickFormatter={(value) => `${value}%`}
            />
            <Tooltip
              formatter={(value) =>
                typeof value === 'number'
                  ? `${value.toFixed(2)}%`
                  : value
              }
            />
            <Bar
              dataKey="projected_soh_percent"
              name="Projected SOH"
              fill="#2563eb"
              label={{
                position: 'top',
                formatter: (value) =>
                  typeof value === 'number' ? `${value.toFixed(2)}%` : '',
              }}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <h3>Counterfactual scenarios</h3>

      <div className="scenario-grid">
        {adaptiveResult.scenarios.map((scenario) => (
          <div className="scenario-card" key={scenario.scenario}>
            <h4>{scenario.scenario}</h4>

            <p>Projected SOH</p>
            <strong>
              {scenario.projected_soh_percent.toFixed(2)}%
            </strong>

            <p>
              Difference vs baseline:{' '}
              {(scenario.difference_vs_baseline * 100).toFixed(2)} pp
            </p>

            <p>
              Assumed recovery:{' '}
              {(scenario.recovery_assumption * 100).toFixed(2)} pp
            </p>
          </div>
        ))}
      </div>
      {adaptiveResult.hybrid_projection && (
        <div className="recommendation-card">
          <p className="eyebrow">EXPERIMENTAL FORECAST</p>
          <h3>SOH Degradation Forecast</h3>
          <p className="chart-caption">
            Experimental linear projection from initial to final SOH.
            Intermediate points are illustrative, not model-generated predictions.
          </p>

          <div style={{ width: '100%', height: 320 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={Array.from(
                  {
                    length:
                      adaptiveResult.hybrid_projection.future_samples + 1,
                  },
                  (_, index) => {
                    const projection = adaptiveResult.hybrid_projection!
                    const initial = projection.initial_soh * 100
                    const final = projection.projected_soh_percent
                    const horizon = projection.future_samples

                    return {
                      sample: index,
                      soh: horizon === 0
                        ? initial
                        : initial + (final - initial) * index / horizon,
                    }
                  },
                )}
                margin={{ top: 10, right: 20, left: 0, bottom: 10 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="sample"
                  tick={{ fontSize: 12 }}
                  label={{
                    value: 'Future observation samples',
                    position: 'insideBottom',
                    offset: -5,
                  }}
                />
                <YAxis
                  domain={[
                    (dataMin: number) => Math.max(0, Math.floor(dataMin - 2)),
                    (dataMax: number) => Math.min(100, Math.ceil(dataMax + 2)),
                  ]}
                  tickFormatter={(value) => `${value}%`}
                />
                <Tooltip
                  formatter={(value) =>
                    typeof value === 'number'
                      ? `${value.toFixed(2)}%`
                      : value
                  }
                  labelFormatter={(label) => `Future sample ${label}`}
                />
                <ReferenceLine
                  y={80}
                  stroke="#dc2626"
                  strokeDasharray="5 5"
                  label="80% reference"
                />
                <Line
                  type="linear"
                  dataKey="soh"
                  name="Illustrative projected SOH"
                  stroke="#f59e0b"
                  strokeWidth={3}
                  dot
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <h3>Hybrid SOH Projection</h3>

          <div className="scenario-detail">
            <span>Initial SOH</span>
            <b>
              {(adaptiveResult.hybrid_projection.initial_soh * 100).toFixed(2)}%
            </b>
          </div>

          <div className="scenario-detail">
            <span>Projected SOH</span>
            <b>
              {adaptiveResult.hybrid_projection.projected_soh_percent.toFixed(2)}%
            </b>
          </div>

          <div className="scenario-detail">
            <span>Forecast horizon</span>
            <b>
              {adaptiveResult.hybrid_projection.future_samples} samples
            </b>
          </div>

          <div className="scenario-detail">
            <span>Hybrid degradation rate</span>
            <b>
              {(adaptiveResult.hybrid_projection.hybrid_degradation_per_sample * 100).toFixed(4)} pp/sample
            </b>
          </div>

          <div className="scenario-detail">
            <span>Trend fit (R²)</span>
            <b>
              {adaptiveResult.hybrid_projection.trend_r_squared === null
                ? 'Unavailable'
                : adaptiveResult.hybrid_projection.trend_r_squared.toFixed(3)}
            </b>
          </div>

          <p className="chart-caption">
            This experimental projection combines a baseline degradation
            assumption with a recent observed trend. Samples are not verified
            physical battery cycles.
          </p>

          <p className="chart-caption">
            Physically validated:{' '}
            {adaptiveResult.hybrid_projection.is_physically_validated
              ? 'Yes'
              : 'No — experimental simulation only'}
          </p>
        </div>
      )}

      
      <div className="recommendation-card">
        <p className="eyebrow">MAINTENANCE AGENT DECISION</p>

        <div className="recommendation-main">
          <div>
            <span className="recommendation-label">Recommended action</span>
            <h3>{adaptiveResult.recommendation.recommended_action}</h3>
          </div>

          <div className="recommendation-soh">
            <span className="recommendation-label">Urgency</span>
            <strong>
              {adaptiveResult.recommendation.urgency.toUpperCase()}
            </strong>
          </div>
        </div>

        <p>{adaptiveResult.recommendation.reason}</p>

        <div className="scenario-detail">
          <span>Selected simulation scenario</span>
          <b>{adaptiveResult.recommendation.recommended_scenario}</b>
        </div>
      

        <div className="scenario-detail">
          <span>Projected SOH</span>
          <b>
            {(adaptiveResult.recommendation.projected_soh * 100).toFixed(2)}%
          </b>
        </div>

        <div className="scenario-detail">
          <span>SOH threshold status</span>
          <b>{adaptiveResult.recommendation.status.replaceAll('_', ' ')}</b>
        </div>

        <h3>Recommended action steps</h3>
        <ol>
          {adaptiveResult.recommendation.action_steps.map((step, index) => (
            <li key={index}>{step}</li>
          ))}
        </ol>

        <h3>Evidence required</h3>
        <ul>
          {adaptiveResult.recommendation.required_evidence.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>

        <p className="chart-caption">
          Rule-based, simulation-informed recommendation. Maintenance effects
          have not been validated in real-world conditions.
        </p>
      </div>
      <div className="scenario-detail">
        <span>Controller type</span>
        <b>{adaptiveResult.controller_type.replaceAll('_', ' ')}</b>
      </div>

      <div className="scenario-detail">
        <span>Maintenance effects validated</span>
        <b>{adaptiveResult.maintenance_effects_validated ? 'Yes' : 'No'}</b>
      </div>

      <h3>Decision factors</h3>
      <ul>
        <li>
          Current SOH below threshold:{' '}
          {adaptiveResult.recommendation.decision_factors.current_soh_below_threshold
            ? 'Yes'
            : 'No'}
        </li>
        <li>
          Degradation trend declining:{' '}
          {adaptiveResult.recommendation.decision_factors.trend_is_declining
            ? 'Yes'
            : 'No'}
        </li>
        <li>
          Rapid degradation detected:{' '}
          {adaptiveResult.recommendation.decision_factors.trend_indicates_rapid_decline
            ? 'Yes'
            : 'No'}
        </li>
        <li>
          Baseline meets SOH threshold:{' '}
          {adaptiveResult.recommendation.decision_factors.baseline_meets_threshold
            ? 'Yes'
            : 'No'}
        </li>
        <li>
          Acceptable scenarios:{' '}
          {adaptiveResult.recommendation.decision_factors.acceptable_scenario_count}
        </li>
      </ul>


      <p className="notice">{adaptiveResult.notice}</p>

      <p className="chart-caption">
        The recommendation uses rule-based logic. Maintenance recovery
        values are illustrative simulation assumptions, not validated
        real-world maintenance effects. Observation order is not confirmed
        physical cycle order.
      </p>
    </>
  )}
</section>

      <footer className="footer">
        <span>VoltTwin</span>
        <span>Software-based EV battery digital twin</span>
      </footer>
    </main>
  )
}

export default App
