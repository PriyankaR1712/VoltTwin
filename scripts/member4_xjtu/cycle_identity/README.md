# XJTU Cycle Identity Audit

This isolated, read-only audit examines evidence connecting prepared XJTU MAT
cycles to SOHbenchmark handcrafted-feature workbook rows. It does not change
the candidate extractor or alignment behavior and does not declare any pair a
verified identity.

## Run

From the repository root in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m scripts.member4_xjtu.cycle_identity.identity_investigation
```

Optional paths:

```powershell
.\.venv\Scripts\python.exe -m scripts.member4_xjtu.cycle_identity.identity_investigation `
  --data-root reference\SOHbenchmark\data\XJTU `
  --output-dir reports\member4_cycle_identity_investigation
```

The audit writes `profile_audit.csv`, `schema_inventory.csv`,
`unmatched_rows_and_cycles.csv`, `mapping_evidence.csv`, and `summary.json`.
Its current-alignment counts come from the existing `_profile_pairs` helper,
which is imported and called unchanged. Same-index capacity comparisons are
reported as supporting label evidence only; unequal-length sequences are not
positionally compared.

Tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests\member4_xjtu\cycle_identity
```

## Evidence classes

- **Authoritatively verified**: direct authoritative identifier or join proof
  for the specific cycle and workbook row.
- **Independently corroborated**: independent evidence supports the claimed
  relationship but does not itself constitute authoritative identity.
- **Diagnostic only**: useful comparison that cannot establish identity.
- **Ambiguous**: multiple candidates or unresolved evidence conflicts.
- **Unsupported**: no suitable evidence in the inspected artifacts.

The audit intentionally does not upgrade positional or capacity matches to
verified identity.
