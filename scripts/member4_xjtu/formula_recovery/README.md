# XJTU Original Formula Recovery Evidence Ledger

This isolated package generates a conservative, reproducible evidence ledger
for the 67 SOHbenchmark XJTU handcrafted feature columns. It records the
existing extractor's expressions only as **candidate interpretations** and
does not modify or reproduce the original benchmark feature generator.

Run from the repository root in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m scripts.member4_xjtu.formula_recovery.recover
```

Outputs:

- `reports/member4_original_formula_recovery.md`
- `reports/member4_original_formula_recovery/feature_evidence.csv`
- `reports/member4_original_formula_recovery/entropy_evidence.csv`
- `reports/member4_original_formula_recovery/source_evidence.csv`
- `reports/member4_original_formula_recovery/search_log.csv`
- `reports/member4_original_formula_recovery/status_summary.json`

The original-equation fields remain explicitly unknown unless direct,
feature-specific evidence is located. A source may be authoritative for a
reader, dataset, or related helper without being authoritative for this
workbook's feature definitions. Candidate numerical agreement is not accepted
as provenance.

Run isolated tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests\member4_xjtu\formula_recovery
```
