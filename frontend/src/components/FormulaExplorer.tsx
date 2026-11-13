import { useEffect, useMemo, useState } from 'react'
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceArea,
  ResponsiveContainer,
  Scatter,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import './FormulaExplorer.css'

const API_BASE = '/api/formula-explorer'
const GROUPS = ['CC', 'dV', 'CV', 'dI', 'Charge'] as const

type FeatureGroup = (typeof GROUPS)[number]
type VerificationStatus =
  | 'source_verified'
  | 'candidate_unverified'
  | 'original_formula_unknown'

type FormulaFeature = {
  name: string
  group: FeatureGroup
  order: number
  signal: string
  segment: string
  candidate_formula: string
  unit: string
  evidence_class: string
  formula_status: string
  assumptions: string
  status: VerificationStatus
  status_label: string
  original_benchmark_formula: string
  mathematical_interpretation: string
  candidate_equation: string
  implementation_used: string
  input_units: Record<string, string>
  output_units: string
  variables: { symbol: string; meaning: string; unit: string }[]
  category_description: string
  research_evidence: { report: string; summary: string }
  calculation_steps: string[]
}

type FeatureResponse = {
  features: FormulaFeature[]
  count: number
  source_verified_count: number
  notice: string
}

type Profile = {
  name: string
  cycle_count: number
}

type Interval = {
  start_min: number
  end_min: number
}

type Segment = {
  selection_method: string
  evidence: string
  note: string
  intervals: Interval[]
}

type SignalPoint = {
  time_min: number
  voltage_v: number
  current_a: number
  temperature_c: number
  selected_raw_sample: boolean
}

type IntervalCalculation = {
  start_time_min: number
  end_time_min: number
  duration_min: number
  raw_sample_count?: number
  sample_count?: number
  panel_count?: number
  first_value?: number
  last_value?: number
  minimum_delta_time_min?: number
  maximum_delta_time_min?: number
  nonuniform_delta_time_count?: number
  trapezoid_sum_before_hour_conversion?: number
  trapezoid_panels?: {
    panel_index: number
    start_time_min: number
    end_time_min: number
    delta_time_min: number
    start_value: number
    end_value: number
    panel_integral: number
  }[]
}

type MomentCalculation = {
  sample_count: number
  mean: number
  variance: number
  standard_deviation: number
  third_central_moment: number
  fourth_central_moment: number
  skewness: number
  pearson_kurtosis: number
}

type CalculationDiagnostics = {
  operation: string
  candidate_result: number | null
  intervals?: { start_time_min: number; end_time_min: number; duration_min: number; raw_sample_count: number }[]
  segment_sample_count?: number
  statistical_grid?: {
    point_count_per_interval: number
    combined_sample_count: number
    combined_mean_elapsed_time_min: number
    intervals: {
      start_time_min: number
      end_time_min: number
      elapsed_time_first_min: number
      elapsed_time_last_min: number
      mean_elapsed_time_min: number
    }[]
  }
  statistical_moments_by_channel?: Record<string, MomentCalculation>
  moments?: MomentCalculation
  integration_by_interval?: IntervalCalculation[]
  trapezoid_sum_before_hour_conversion?: number
  hour_conversion_divisor?: number
  interval_durations_min?: number[]
  combined_duration_min?: number
  is_disjoint?: boolean
  start_time_min?: number
  end_time_min?: number
  start_voltage_v?: number
  end_voltage_v?: number
  delta_voltage_v?: number
  start_current_a?: number
  end_current_a?: number
  delta_current_a?: number
  duration_min?: number
  candidate_rate_v_per_min?: number | null
  candidate_rate_a_per_min?: number | null
  sample_count?: number
  bin_count?: number
  bin_edges?: number[]
  nonzero_bin_indices?: number[]
  nonzero_bin_counts?: number[]
  nonzero_bin_probabilities?: number[]
  entropy_contributions?: number[]
  entropy_nats?: number
}

type CalculationResponse = {
  batch: number
  profile: string
  cycle: number
  capacity_label: number
  is_candidate_calculation: boolean
  values_are_original_benchmark_values: boolean
  trace: {
    time_min: number[]
    voltage_v: number[]
    current_a: number[]
    temperature_c: number[]
  }
  segments: Record<FeatureGroup, Segment>
  feature_values: Record<string, number | null>
  calculation_detail: {
    feature: FormulaFeature
    intermediate_calculation: CalculationDiagnostics | null
    candidate_result: number | null
  }
  calculation_details: Record<string, CalculationDiagnostics>
  raw_sample_indices_by_group: Record<FeatureGroup, number[]>
  raw_sample_delta_time_min: number[]
  raw_sampling: {
    sample_count: number
    minimum_delta_time_min: number
    maximum_delta_time_min: number
    median_delta_time_min: number
    is_uniform: boolean
  }
  notice: string
}

type PlotLine = {
  key: keyof Omit<SignalPoint, 'time_min'>
  label: string
  color: string
  yAxisId: 'left' | 'right'
}

function isFeatureResponse(value: FeatureResponse): boolean {
  return value.count === 67 && value.features.length === 67
}

async function fetchJson<T>(url: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(url, { signal })
  let payload: { detail?: string } & Record<string, unknown>

  try {
    payload = await response.json()
  } catch {
    throw new Error('The Formula Explorer API returned an invalid response.')
  }

  if (!response.ok) {
    throw new Error(
      typeof payload.detail === 'string'
        ? payload.detail
        : `The Formula Explorer API request failed (${response.status}).`,
    )
  }

  return payload as T
}

function statusLabel(status: VerificationStatus): string {
  if (status === 'source_verified') return 'Source verified'
  if (status === 'original_formula_unknown') return 'Original formula unknown'
  return 'Candidate / Unverified'
}

function plotLinesFor(feature: FormulaFeature): PlotLine[] {
  if (feature.name.endsWith('_energy')) {
    return [
      { key: 'voltage_v', label: 'Voltage (V)', color: '#78e4c2', yAxisId: 'left' },
      { key: 'current_a', label: 'Current (A)', color: '#f4b76b', yAxisId: 'right' },
    ]
  }
  if (feature.signal.toLowerCase().includes('voltage')) {
    return [{ key: 'voltage_v', label: 'Voltage (V)', color: '#78e4c2', yAxisId: 'left' }]
  }
  if (feature.signal.toLowerCase().includes('current')) {
    return [{ key: 'current_a', label: 'Current (A)', color: '#f4b76b', yAxisId: 'left' }]
  }
  if (feature.signal.toLowerCase().includes('temperature')) {
    return [{ key: 'temperature_c', label: 'Temperature (°C)', color: '#a99bff', yAxisId: 'left' }]
  }
  return [
    { key: 'voltage_v', label: 'Voltage context (V)', color: '#78e4c2', yAxisId: 'left' },
    { key: 'current_a', label: 'Current context (A)', color: '#f4b76b', yAxisId: 'right' },
  ]
}

function makeSignalPoints(
  trace: CalculationResponse['trace'],
  selectedIndices: number[],
): SignalPoint[] {
  const selected = new Set(selectedIndices)
  return trace.time_min.map((time, index) => ({
    time_min: time,
    voltage_v: trace.voltage_v[index],
    current_a: trace.current_a[index],
    temperature_c: trace.temperature_c[index],
    selected_raw_sample: selected.has(index),
  }))
}

function formatValue(value: number): string {
  return new Intl.NumberFormat(undefined, {
    maximumSignificantDigits: 7,
  }).format(value)
}

function DiagnosticRows({
  feature,
  diagnostic,
}: {
  feature: FormulaFeature
  diagnostic: CalculationDiagnostics | undefined
}) {
  if (!diagnostic) {
    return (
      <p className="formula-inline-state">
        No candidate calculation details are available for this feature and cycle.
        The candidate segment may not have been detected.
      </p>
    )
  }

  const result = diagnostic.candidate_result
  const rows: { label: string; value: string }[] = []
  const operation = diagnostic.operation

  if (operation === 'trapezoidal_time_integration') {
    const integrandUnit = feature.name.endsWith('_energy') ? 'W' : 'A'
    for (const [index, part] of (diagnostic.integration_by_interval ?? []).entries()) {
      rows.push(
        {
          label: `Interval ${index + 1}`,
          value: `${formatValue(part.start_time_min)}–${formatValue(part.end_time_min)} min`,
        },
        {
          label: `Raw samples / trapezoid panels`,
          value: `${part.sample_count ?? '—'} / ${part.panel_count ?? '—'}`,
        },
        {
          label: `Δt range`,
          value: `${formatValue(part.minimum_delta_time_min ?? 0)}–${formatValue(part.maximum_delta_time_min ?? 0)} min`,
        },
        {
          label: `First / last integrand`,
          value: `${formatValue(part.first_value ?? 0)} / ${formatValue(part.last_value ?? 0)} ${integrandUnit}`,
        },
      )
    }
    rows.push(
      {
        label: 'Sum of trapezoid panels',
        value: `${formatValue(diagnostic.trapezoid_sum_before_hour_conversion ?? 0)} ${integrandUnit}·min`,
      },
      {
        label: 'Hour conversion',
        value: `÷ ${formatValue(diagnostic.hour_conversion_divisor ?? 60)} min/h`,
      },
    )
  } else if (operation === 'arithmetic_mean_of_elapsed_time') {
    const grid = diagnostic.statistical_grid
    rows.push(
      { label: 'Uniform points per interval', value: String(grid?.point_count_per_interval ?? '—') },
      { label: 'Total elapsed-time samples', value: String(grid?.combined_sample_count ?? '—') },
      {
        label: 'Mean elapsed time',
        value: `${formatValue(grid?.combined_mean_elapsed_time_min ?? result ?? 0)} min`,
      },
    )
    grid?.intervals.forEach((interval, index) => {
      rows.push({
        label: `Interval ${index + 1} elapsed range`,
        value: `${formatValue(interval.elapsed_time_first_min)}–${formatValue(interval.elapsed_time_last_min)} min`,
      })
    })
  } else if (['mean', 'std', 'skewness', 'kurtosis'].includes(operation)) {
    const moments = diagnostic.moments
    rows.push(
      { label: 'Uniform-grid sample count', value: String(moments?.sample_count ?? '—') },
      { label: 'Mean μₓ', value: formatValue(moments?.mean ?? 0) },
    )
    if (operation !== 'mean') {
      rows.push(
        { label: 'Population variance m₂', value: formatValue(moments?.variance ?? 0) },
        { label: 'Standard deviation σₓ', value: formatValue(moments?.standard_deviation ?? 0) },
      )
    }
    if (operation === 'skewness') {
      rows.push({
        label: 'Third central moment m₃',
        value: formatValue(moments?.third_central_moment ?? 0),
      })
    } else if (operation === 'kurtosis') {
      rows.push({
        label: 'Fourth central moment m₄',
        value: formatValue(moments?.fourth_central_moment ?? 0),
      })
    }
    rows.push({
      label: 'Candidate statistic',
      value: `${formatValue(result ?? 0)} ${feature.output_units}`,
    })
  } else if (operation === 'entropy') {
    rows.push(
      { label: 'Selected raw segment samples', value: String(diagnostic.segment_sample_count ?? '—') },
      {
        label: 'Uniform-time grid points per interval',
        value: String(diagnostic.statistical_grid?.point_count_per_interval ?? '—'),
      },
      { label: 'Histogram samples', value: String(diagnostic.sample_count ?? '—') },
      { label: 'Diagnostic bins', value: String(diagnostic.bin_count ?? '—') },
      { label: 'Non-empty bin count', value: String(diagnostic.nonzero_bin_counts?.length ?? '—') },
      { label: 'Σ −pᵦ ln(pᵦ)', value: `${formatValue(diagnostic.entropy_nats ?? result ?? 0)} nats` },
    )
  } else if (operation === 'candidate_endpoint_rate') {
    const signalSymbol = feature.name.startsWith('dV_') ? 'V' : 'I'
    const signalUnit = signalSymbol === 'V' ? 'V' : 'A'
    rows.push(
      { label: 'Start signal', value: `${formatValue(diagnostic.start_voltage_v ?? diagnostic.start_current_a ?? 0)} ${signalUnit}` },
      { label: 'End signal', value: `${formatValue(diagnostic.end_voltage_v ?? diagnostic.end_current_a ?? 0)} ${signalUnit}` },
      { label: 'Signal difference', value: `${formatValue(diagnostic.delta_voltage_v ?? diagnostic.delta_current_a ?? 0)} ${signalUnit}` },
      { label: 'Interval duration', value: `${formatValue(diagnostic.duration_min ?? 0)} min` },
      { label: 'Endpoint difference ÷ duration', value: `${formatValue(result ?? 0)} ${feature.output_units}` },
    )
  } else if (operation === 'sum_of_interval_durations') {
    rows.push(
      { label: 'Candidate intervals', value: String(diagnostic.interval_durations_min?.length ?? 0) },
      { label: 'Interval durations', value: (diagnostic.interval_durations_min ?? []).map(formatValue).join(' + ') || 'None' },
      { label: 'Combined duration', value: result === null ? 'Unavailable for disjoint intervals' : `${formatValue(result)} min` },
    )
  }

  return (
    <div className="formula-derivation-content">
      <div className="formula-derivation-table">
        {rows.map((row, index) => (
          <div className="formula-derivation-row" key={`${row.label}-${index}`}>
            <span>{row.label}</span>
            <strong>{row.value}</strong>
          </div>
        ))}
      </div>
      {operation === 'trapezoidal_time_integration' && (
        <details className="formula-segment-details">
          <summary>Show each trapezoid panel substitution</summary>
          {(diagnostic.integration_by_interval ?? []).map((part, intervalIndex) => (
            <div className="formula-panel-table" key={intervalIndex}>
              <div className="formula-panel-table-head">
                <span>Panel</span><span>Δt (min)</span><span>Start / end integrand</span>
                <span>½ × (start + end) × Δt</span>
              </div>
              {(part.trapezoid_panels ?? []).map((panel) => (
                <div key={panel.panel_index}>
                  <span>{panel.panel_index}</span>
                  <span>{formatValue(panel.delta_time_min)}</span>
                  <span>{formatValue(panel.start_value)} / {formatValue(panel.end_value)}</span>
                  <span>
                    ½ × ({formatValue(panel.start_value)} + {formatValue(panel.end_value)})
                    {' '}× {formatValue(panel.delta_time_min)} = {formatValue(panel.panel_integral)}
                  </span>
                </div>
              ))}
            </div>
          ))}
        </details>
      )}
      {operation === 'entropy' && diagnostic.bin_edges && (
        <details className="formula-segment-details">
          <summary>Show histogram bin probabilities and contributions</summary>
          <div className="formula-entropy-table">
            {(diagnostic.nonzero_bin_counts ?? []).map((count, index) => (
              <div key={index}>
                <span>
                  Bin {(diagnostic.nonzero_bin_indices?.[index] ?? index) + 1}
                </span>
                <span>
                  {formatValue(diagnostic.bin_edges?.[diagnostic.nonzero_bin_indices?.[index] ?? index] ?? 0)}
                  –{formatValue(diagnostic.bin_edges?.[(diagnostic.nonzero_bin_indices?.[index] ?? index) + 1] ?? 0)}
                </span>
                <span>{count} samples</span>
                <span>p = {formatValue(diagnostic.nonzero_bin_probabilities?.[index] ?? 0)}</span>
                <span>−p ln p = {formatValue(diagnostic.entropy_contributions?.[index] ?? 0)}</span>
              </div>
            ))}
          </div>
        </details>
      )}
      <p className="formula-substitution">
        Substitution uses the selected raw cycle. The reported result is the
        existing extractor output, not a reconstruction in the browser.
      </p>
    </div>
  )
}

export default function FormulaExplorer() {
  const [features, setFeatures] = useState<FormulaFeature[]>([])
  const [selectedName, setSelectedName] = useState('')
  const [selectedGroup, setSelectedGroup] = useState<'All' | FeatureGroup>('All')
  const [search, setSearch] = useState('')
  const [featureLoading, setFeatureLoading] = useState(true)
  const [featureError, setFeatureError] = useState('')
  const [batch, setBatch] = useState(1)
  const [profiles, setProfiles] = useState<Profile[]>([])
  const [profile, setProfile] = useState('')
  const [cycle, setCycle] = useState(1)
  const [catalogLoading, setCatalogLoading] = useState(true)
  const [catalogError, setCatalogError] = useState('')
  const [calculation, setCalculation] = useState<CalculationResponse | null>(null)
  const [calculationLoading, setCalculationLoading] = useState(false)
  const [calculationError, setCalculationError] = useState('')

  useEffect(() => {
    const controller = new AbortController()
    fetchJson<FeatureResponse>(`${API_BASE}/features`, controller.signal)
      .then((response) => {
        if (!isFeatureResponse(response)) {
          throw new Error('The API did not return the complete 67-feature schema.')
        }
        setFeatures(response.features)
        setSelectedName(response.features[0]?.name ?? '')
      })
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === 'AbortError') return
        setFeatureError(
          error instanceof Error ? error.message : 'Could not load feature definitions.',
        )
      })
      .finally(() => {
        if (!controller.signal.aborted) setFeatureLoading(false)
      })

    return () => controller.abort()
  }, [])

  useEffect(() => {
    const controller = new AbortController()
    fetchJson<{ profiles: Profile[] }>(
      `${API_BASE}/batches/${batch}/profiles`,
      controller.signal,
    )
      .then((response) => {
        setProfiles(response.profiles)
        setProfile(response.profiles[0]?.name ?? '')
        setCycle(1)
      })
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === 'AbortError') return
        setCatalogError(
          error instanceof Error ? error.message : 'Could not load XJTU profiles.',
        )
      })
      .finally(() => {
        if (!controller.signal.aborted) setCatalogLoading(false)
      })

    return () => controller.abort()
  }, [batch])

  function changeBatch(nextBatch: number) {
    setBatch(nextBatch)
    setCatalogLoading(true)
    setCatalogError('')
    setProfiles([])
    setProfile('')
    setCalculation(null)
    setCalculationError('')
  }

  const selectedFeature = useMemo(
    () => features.find((feature) => feature.name === selectedName) ?? features[0],
    [features, selectedName],
  )

  const filteredFeatures = useMemo(() => {
    const query = search.trim().toLowerCase()
    return features.filter(
      (feature) =>
        (selectedGroup === 'All' || feature.group === selectedGroup) &&
        (!query || feature.name.toLowerCase().includes(query)),
    )
  }, [features, search, selectedGroup])

  const statusCounts = useMemo(
    () => ({
      sourceVerified: features.filter((feature) => feature.status === 'source_verified').length,
      candidate: features.filter((feature) => feature.status === 'candidate_unverified').length,
      unknown: features.filter((feature) => feature.status === 'original_formula_unknown').length,
    }),
    [features],
  )

  const selectedProfile = profiles.find((item) => item.name === profile)
  const selectedSegment = selectedFeature
    ? calculation?.segments[selectedFeature.group]
    : undefined
  const selectedValue = selectedFeature
    ? calculation?.feature_values[selectedFeature.name]
    : undefined
  const selectedDiagnostic = selectedFeature
    ? calculation?.calculation_details[selectedFeature.name]
    : undefined
  const selectedSampleIndices = selectedFeature
    ? calculation?.raw_sample_indices_by_group[selectedFeature.group] ?? []
    : []
  const signalPoints = calculation
    ? makeSignalPoints(calculation.trace, selectedSampleIndices)
    : []
  const plotLines = selectedFeature ? plotLinesFor(selectedFeature) : []

  async function loadCandidateCalculation() {
    if (!selectedProfile || !Number.isInteger(cycle) || cycle < 1) {
      setCalculationError('Select a valid profile and a positive whole-number cycle.')
      return
    }

    setCalculationLoading(true)
    setCalculationError('')
    setCalculation(null)
    const query = new URLSearchParams({
      batch: String(batch),
      profile,
      cycle: String(cycle),
      feature_name: selectedName,
    })

    try {
      const response = await fetchJson<CalculationResponse>(
        `${API_BASE}/calculate?${query.toString()}`,
      )
      setCalculation(response)
    } catch (error) {
      setCalculationError(
        error instanceof Error
          ? error.message
          : 'Could not calculate candidate features for this cycle.',
      )
    } finally {
      setCalculationLoading(false)
    }
  }

  return (
    <div className="formula-explorer">
      <div className="formula-intro">
        <div>
          <p className="formula-eyebrow">XJTU HANDCRAFTED FEATURES</p>
          <h2>Formula Explorer</h2>
          <p>
            Inspect the candidate calculations, input signals, and phase windows
            behind the 67 feature names.
          </p>
        </div>
        <div className="formula-count">
          <strong>{features.length || 67}</strong>
          <span>features</span>
        </div>
      </div>

      <div className="formula-warning" role="note">
        <strong>Formula provenance warning</strong>
        <span>
          Original XJTU workbook formulas have not been verified. Any formula
          shown as a candidate is an approximation, not an author-confirmed
          definition.
        </span>
      </div>

      <div className="formula-status-legend" aria-label="Formula verification status counts">
        <span>
          <i className="source_verified" />
          Source verified · {statusCounts.sourceVerified}
        </span>
        <span>
          <i className="candidate_unverified" />
          Candidate / Unverified · {statusCounts.candidate}
        </span>
        <span>
          <i className="original_formula_unknown" />
          Original formula unknown · {statusCounts.unknown}
        </span>
      </div>

      {featureError && (
        <div className="formula-error" role="alert">
          {featureError} Check that the FastAPI backend is running.
        </div>
      )}

      <div className="formula-workspace">
        <aside className="formula-browser" aria-label="Feature browser">
          <label className="formula-search-label">
            Search features
            <input
              type="search"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search all 67 feature names"
              aria-label="Search all 67 features"
            />
          </label>

          <div className="formula-groups" aria-label="Feature category">
            {(['All', ...GROUPS] as const).map((group) => (
              <button
                type="button"
                key={group}
                className={selectedGroup === group ? 'active' : ''}
                aria-pressed={selectedGroup === group}
                onClick={() => setSelectedGroup(group)}
              >
                {group}
              </button>
            ))}
          </div>

          <div className="formula-list-heading">
            <span>{featureLoading ? 'Loading features…' : `${filteredFeatures.length} features`}</span>
            <span>67 total</span>
          </div>

          <div className="formula-feature-list">
            {filteredFeatures.map((feature) => (
              <button
                type="button"
                key={feature.name}
                className={`formula-feature-row ${selectedName === feature.name ? 'selected' : ''}`}
                onClick={() => setSelectedName(feature.name)}
                aria-current={selectedName === feature.name ? 'true' : undefined}
              >
                <span className="formula-feature-name">{feature.name}</span>
                <span className={`formula-status-dot ${feature.status}`} aria-hidden="true" />
              </button>
            ))}
            {!featureLoading && !featureError && filteredFeatures.length === 0 && (
              <p className="formula-empty">No features match this search.</p>
            )}
          </div>
        </aside>

        <section className="formula-detail" aria-live="polite">
          {featureLoading ? (
            <div className="formula-empty-state">Loading feature definitions…</div>
          ) : selectedFeature ? (
            <>
              <div className="formula-detail-header">
                <div>
                  <span className="formula-category">{selectedFeature.group}</span>
                  <p className="formula-order">Feature {selectedFeature.order} of 67</p>
                </div>
                <span className={`formula-status-badge ${selectedFeature.status}`}>
                  {statusLabel(selectedFeature.status)}
                </span>
              </div>

              <h3 className="formula-feature-title">{selectedFeature.name}</h3>

              <div className="formula-unknown-note">
                Original formula not verified. The expression below describes
                the existing candidate implementation only.
              </div>

              <article className="formula-card">
                <h4>Original benchmark formula</h4>
                <p className="formula-original-unavailable">
                  {selectedFeature.original_benchmark_formula}
                </p>
                <h4 className="formula-subheading">Candidate mathematical notation</h4>
                <code className="formula-equation">{selectedFeature.candidate_equation}</code>
                <p className="formula-plain">
                  <strong>Candidate interpretation:</strong>{' '}
                  {selectedFeature.mathematical_interpretation}
                </p>
                <p className="formula-plain">
                  <strong>Implementation in this project:</strong>{' '}
                  {selectedFeature.implementation_used}
                </p>
                <p className="formula-unit">
                  Input units: {Object.entries(selectedFeature.input_units)
                    .map(([name, unit]) => `${name} (${unit})`)
                    .join(', ') || 'Not specified'}
                  {' · '}Output unit: {selectedFeature.output_units}
                </p>
              </article>

              <div className="formula-two-column">
                <article className="formula-card">
                  <h4>Input signals and segment</h4>
                  <dl className="formula-definitions">
                    <div>
                      <dt>Input signal</dt>
                      <dd>{selectedFeature.signal}</dd>
                    </div>
                    <div>
                      <dt>Category meaning</dt>
                      <dd>{selectedFeature.category_description}</dd>
                    </div>
                    <div>
                      <dt>Candidate segment</dt>
                      <dd>{selectedFeature.segment}</dd>
                    </div>
                  </dl>
                </article>

                <article className="formula-card">
                  <h4>Calculation steps</h4>
                  <ol className="formula-steps">
                    {selectedFeature.calculation_steps.map((step, index) => (
                      <li key={`${selectedFeature.name}-${index}`}>{step}</li>
                    ))}
                  </ol>
                </article>
              </div>

              <article className="formula-card">
                <h4>Variables and units</h4>
                <div className="formula-variable-table">
                  {selectedFeature.variables.map((variable) => (
                    <div key={variable.symbol}>
                      <code>{variable.symbol}</code>
                      <span>{variable.meaning}</span>
                      <strong>{variable.unit}</strong>
                    </div>
                  ))}
                </div>
              </article>

              {selectedFeature.status === 'original_formula_unknown' && (
                <div className="formula-unknown-note">
                  Original formula unknown. The displayed histogram expression
                  is a diagnostic proxy; its signal and entropy convention are
                  not verified for the Excel feature.
                </div>
              )}

              <article className="formula-card formula-sample-card">
                <div className="formula-card-heading">
                  <div>
                    <h4>Run candidate calculation on a raw cycle</h4>
                    <p>
                      Results come from the Member 4 extractor and are not
                      benchmark workbook values.
                    </p>
                  </div>
                  <span className="formula-candidate-tag">Candidate only</span>
                </div>

                <div className="formula-sample-controls">
                  <label>
                    Batch
                    <select
                      value={batch}
                      onChange={(event) => changeBatch(Number(event.target.value))}
                      disabled={catalogLoading}
                    >
                      {Array.from({ length: 6 }, (_, index) => index + 1).map(
                        (batchNumber) => (
                          <option key={batchNumber} value={batchNumber}>
                            Batch {batchNumber}
                          </option>
                        ),
                      )}
                    </select>
                  </label>
                  <label>
                    Battery profile
                    <select
                      value={profile}
                      onChange={(event) => {
                        setProfile(event.target.value)
                        setCycle(1)
                        setCalculation(null)
                        setCalculationError('')
                      }}
                      disabled={catalogLoading || profiles.length === 0}
                    >
                      {profiles.map((item) => (
                        <option key={item.name} value={item.name}>
                          {item.name} ({item.cycle_count} cycles)
                        </option>
                      ))}
                    </select>
                  </label>
                  <label>
                    Cycle
                    <input
                      type="number"
                      min="1"
                      max={selectedProfile?.cycle_count}
                      step="1"
                      value={cycle}
                      onChange={(event) => {
                        setCycle(Number(event.target.value))
                        setCalculation(null)
                        setCalculationError('')
                      }}
                      disabled={!selectedProfile || catalogLoading}
                    />
                  </label>
                  <button
                    type="button"
                    className="formula-run-button"
                    onClick={loadCandidateCalculation}
                    disabled={
                      catalogLoading ||
                      calculationLoading ||
                      !selectedProfile ||
                      !Number.isInteger(cycle) ||
                      cycle < 1 ||
                      cycle > (selectedProfile?.cycle_count ?? 0)
                    }
                  >
                    {calculationLoading ? 'Calculating…' : 'Calculate candidate'}
                  </button>
                </div>

                {catalogLoading && (
                  <p className="formula-inline-state" role="status">
                    Loading available profiles…
                  </p>
                )}
                {catalogError && (
                  <p className="formula-error" role="alert">{catalogError}</p>
                )}
                {calculationError && (
                  <p className="formula-error" role="alert">{calculationError}</p>
                )}

                {calculation && (
                  <div className="formula-calculation-result">
                    <div className="formula-value-card">
                      <span>Candidate result · {selectedFeature.name}</span>
                      {typeof selectedValue === 'number' && Number.isFinite(selectedValue) ? (
                        <strong>
                          {formatValue(selectedValue)}
                          <small>{selectedFeature.unit}</small>
                        </strong>
                      ) : (
                        <strong className="formula-unavailable">
                          Not available for this cycle
                        </strong>
                      )}
                      <p>
                        {calculation.profile}, batch {calculation.batch}, cycle{' '}
                        {calculation.cycle} · capacity label{' '}
                        {formatValue(calculation.capacity_label)} Ah
                      </p>
                    </div>

                    <div className="formula-result-warning">
                      Candidate calculation only. It may differ from the
                      original benchmark workbook implementation.
                    </div>

                    <div className="formula-plot-heading">
                      <div>
                        <h5>Raw cycle signals and calculation samples</h5>
                        <p>
                          Shading shows the candidate interval; markers identify
                          raw samples selected in the plotted group. Series are
                          raw MAT values; interpolation is used only inside the
                          candidate calculation.
                        </p>
                      </div>
                      <span>{selectedSegment?.selection_method ?? 'No interval'}</span>
                    </div>

                    <div className="formula-sampling-summary">
                      <span>Raw samples: {calculation.raw_sampling.sample_count}</span>
                      <span>
                        Δt min / median / max:{' '}
                        {formatValue(calculation.raw_sampling.minimum_delta_time_min)} /{' '}
                        {formatValue(calculation.raw_sampling.median_delta_time_min)} /{' '}
                        {formatValue(calculation.raw_sampling.maximum_delta_time_min)} min
                      </span>
                      <span>
                        Selected raw samples: {selectedSampleIndices.length}
                      </span>
                      <span>
                        Sampling: {calculation.raw_sampling.is_uniform ? 'uniform' : 'nonuniform'}
                      </span>
                    </div>

                    {signalPoints.length > 0 ? (
                      <div className="formula-chart">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={signalPoints} margin={{ top: 8, right: 12, bottom: 4, left: 0 }}>
                            <CartesianGrid stroke="#293749" strokeDasharray="3 3" />
                            <XAxis
                              dataKey="time_min"
                              type="number"
                              domain={['dataMin', 'dataMax']}
                              tickFormatter={(value: number) => value.toFixed(1)}
                              stroke="#8190a4"
                              tick={{ fontSize: 11 }}
                              label={{
                                value: 'Time (min)',
                                position: 'insideBottom',
                                offset: -2,
                                fill: '#9eacc0',
                                fontSize: 11,
                              }}
                            />
                            <YAxis
                              yAxisId="left"
                              stroke="#8190a4"
                              tick={{ fontSize: 11 }}
                              width={48}
                            />
                            {plotLines.some((line) => line.yAxisId === 'right') && (
                              <YAxis
                                yAxisId="right"
                                orientation="right"
                                stroke="#8190a4"
                                tick={{ fontSize: 11 }}
                                width={48}
                              />
                            )}
                            <Tooltip
                              labelFormatter={(value) => `Time: ${Number(value).toFixed(3)} min`}
                              contentStyle={{
                                background: '#101a27',
                                border: '1px solid #35465b',
                                borderRadius: 8,
                                color: '#e8edf6',
                              }}
                            />
                            <Legend />
                            {selectedSegment?.intervals.map((interval, index) => (
                              <ReferenceArea
                                key={`${interval.start_min}-${index}`}
                                x1={interval.start_min}
                                x2={interval.end_min}
                                fill="#78e4c2"
                                fillOpacity={0.14}
                                strokeOpacity={0}
                              />
                            ))}
                            {plotLines.map((line) => (
                              <Line
                                key={line.key}
                                type="monotone"
                                dataKey={line.key}
                                name={line.label}
                                stroke={line.color}
                                strokeWidth={2}
                                yAxisId={line.yAxisId}
                                dot={false}
                                activeDot={{ r: 4 }}
                                isAnimationActive={false}
                              />
                            ))}
                            {plotLines.map((line) => (
                              <Scatter
                                key={`${line.key}-selected-samples`}
                                data={signalPoints.filter((point) => point.selected_raw_sample)}
                                dataKey={line.key}
                                name={`${line.label} selected raw samples`}
                                xAxisId={0}
                                yAxisId={line.yAxisId}
                                fill={line.color}
                                shape="circle"
                                legendType="none"
                              />
                            ))}
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    ) : (
                      <p className="formula-inline-state">No signal samples are available to plot.</p>
                    )}

                    <details className="formula-segment-details">
                      <summary>Candidate segment selection evidence</summary>
                      <p>{selectedSegment?.evidence ?? 'No segment information returned.'}</p>
                      <p>{selectedSegment?.note ?? ''}</p>
                      <p>
                        Candidate segment description: {selectedFeature.segment}
                      </p>
                      {selectedSegment?.intervals.length === 0 && (
                        <p>No candidate interval was found for this segment.</p>
                      )}
                    </details>

                    <details className="formula-segment-details">
                      <summary>View selected raw MAT samples</summary>
                      <div className="formula-raw-table">
                        <div className="formula-raw-table-head">
                          <span>Index</span><span>Time (min)</span><span>Voltage (V)</span>
                          <span>Current (A)</span><span>Temperature (°C)</span>
                        </div>
                        {selectedSampleIndices.map((index) => (
                          <div key={index}>
                            <span>{index}</span>
                            <span>{formatValue(calculation.trace.time_min[index])}</span>
                            <span>{formatValue(calculation.trace.voltage_v[index])}</span>
                            <span>{formatValue(calculation.trace.current_a[index])}</span>
                            <span>{formatValue(calculation.trace.temperature_c[index])}</span>
                          </div>
                        ))}
                        {selectedSampleIndices.length === 0 && (
                          <p>No raw samples meet the candidate segment mask.</p>
                        )}
                      </div>
                    </details>

                    <section className="formula-derivation">
                      <div className="formula-derivation-heading">
                        <div>
                          <p className="formula-eyebrow">NUMERICAL DERIVATION</p>
                          <h5>Candidate substitution and intermediate values</h5>
                        </div>
                        <span className={`formula-status-badge ${selectedFeature.status}`}>
                          {selectedFeature.status_label}
                        </span>
                      </div>
                      <p className="formula-derivation-equation">
                        {selectedFeature.candidate_equation}
                      </p>
                      <DiagnosticRows
                        feature={selectedFeature}
                        diagnostic={selectedDiagnostic}
                      />
                      <p className="formula-derivation-final">
                        Final candidate value:{' '}
                        {typeof selectedValue === 'number'
                          ? `${formatValue(selectedValue)} ${selectedFeature.output_units}`
                          : 'Unavailable for this cycle'}
                      </p>
                      <p className="formula-original-unavailable">
                        Original benchmark formula: unavailable; original formula
                        not verified.
                      </p>
                    </section>
                  </div>
                )}
              </article>

              <details className="formula-assumptions">
                <summary>Evidence and assumptions</summary>
                <p>Original benchmark formula: {selectedFeature.original_benchmark_formula}</p>
                <p>{selectedFeature.formula_status}</p>
                <p>{selectedFeature.assumptions}</p>
                <p>{selectedFeature.research_evidence.summary}</p>
                <p>
                  Research source: <code>{selectedFeature.research_evidence.report}</code>
                </p>
                <p>
                  Numerical agreement with Excel is not proof of the original
                  formula. See the formula research and candidate validation
                  reports for evidence and alignment limitations.
                </p>
              </details>
            </>
          ) : (
            <div className="formula-empty-state">
              {featureError || 'Select a feature to inspect its candidate definition.'}
            </div>
          )}
        </section>
      </div>
    </div>
  )
}
