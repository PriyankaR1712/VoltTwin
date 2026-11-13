# Member 4 XJTU Candidate Extractor

This package independently extracts candidate values for the 67 workbook columns from
the benchmark's prepared XJTU MAT traces. It does not claim to reproduce the original
workbook generator. Every computed feature is unverified until its original formula
and segment convention are supported by an authoritative source.

## Data and signal assumptions

The prepared MAT cycles expose `relative_time_min`, `voltage_V`, `current_A`,
`temperature_C`, and a scalar `capacity` label. The observed charge traces have 128
samples and nonuniform time spacing. Integration therefore uses the stored timestamps;
the candidate statistics use explicit uniform-time interpolation. Neither choice is
known to match the original spreadsheet implementation.

## Candidate segmentation

- CC defaults to the adaptive 97.5%-of-95th-percentile current plateau with a 4.199 V
  voltage ceiling. Use `--cc-method author_documented` to instead apply the
  author-helper selector (`current >= 3.9 A` and `voltage <= 4.199 V`). Neither is
  established as the workbook's CC definition.
- CV begins at the first rising crossing of 4.199 V and ends at the stored trace end.
- dV uses a candidate rising 3.9-4.0 V window within CC; dI uses a candidate falling
  1.0-0.9 A window within CV. Their original boundaries are unknown.
- Charge is the full stored charge trace.

Missing or disjoint candidate windows are reported as unavailable for boundary-dependent
features; intervals are not silently bridged. Entropy is a diagnostic histogram proxy,
not a recovered formula.

## Commands

Run all-batch candidate comparison with:

```powershell
.\.venv\Scripts\python.exe -m scripts.member4_xjtu.validate
```

This writes `reports/member4_candidate_validation.csv` and
`reports/member4_candidate_validation.md`. To produce per-cycle candidate values:

```powershell
.\.venv\Scripts\python.exe -m scripts.member4_xjtu.extract
```

The per-cycle CSV includes raw profile/cycle identifiers, capacity label, selected
segment method/state, interval metadata, an explicit unverified-candidate status, and
the 67 values. `entropy_status` marks the four entropy columns as unknown-original-
formula histogram proxies. Detailed formulas, evidence classes, and assumptions are in
the validation CSV and report rather than repeated in every cycle row. The workbook
alignment used for comparison is only diagnostic: equal-count profiles are paired
positionally with an explicit unverified status; unequal-count profiles require a
unique monotone capacity match, and ambiguous rows are excluded.
