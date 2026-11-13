from __future__ import annotations

import json
import warnings
from itertools import combinations
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from .analysis_data import load_candidate_frame
from .feature_definitions import FEATURE_NAMES
from .loader import DEFAULT_DATA_ROOT

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
REPORT_ROOT = REPOSITORY_ROOT / "reports" / "member4"
DEFAULT_REPORT = REPORT_ROOT / "feature_aging_analysis.md"
DEFAULT_SUMMARY = REPORT_ROOT / "feature_aging_summary.json"
DEFAULT_FIGURES = REPORT_ROOT / "aging_figures"
MIN_PROFILE_CYCLES_FOR_RHO = 5
MIN_PROFILES_FOR_CORRELATION = 10


def _spearman(x: pd.Series | np.ndarray, y: pd.Series | np.ndarray) -> float | None:
    left = np.asarray(x, dtype=np.float64)
    right = np.asarray(y, dtype=np.float64)
    finite = np.isfinite(left) & np.isfinite(right)
    left = left[finite]
    right = right[finite]
    if (
        len(left) < MIN_PROFILE_CYCLES_FOR_RHO
        or len(np.unique(left)) < 2
        or len(np.unique(right)) < 2
    ):
        return None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = spearmanr(left, right)
    rho = float(result.statistic)
    return rho if np.isfinite(rho) else None


def _median_or_none(values: list[float]) -> float | None:
    return float(np.median(values)) if values else None


def _feature_profile_trends(
    frame: pd.DataFrame,
) -> list[dict[str, Any]]:
    trend_rows: list[dict[str, Any]] = []
    grouped = frame.groupby("cell_id", sort=True)
    for feature in FEATURE_NAMES:
        cycle_rhos: list[float] = []
        capacity_rhos: list[float] = []
        for _, profile in grouped:
            values = pd.to_numeric(profile[feature], errors="coerce")
            cycle_rho = _spearman(profile["cycle_index"], values)
            capacity_rho = _spearman(profile["capacity_label"], values)
            if cycle_rho is not None:
                cycle_rhos.append(cycle_rho)
            if capacity_rho is not None:
                capacity_rhos.append(capacity_rho)
        directional = max(
            sum(rho > 0 for rho in cycle_rhos),
            sum(rho < 0 for rho in cycle_rhos),
        ) / len(cycle_rhos) if cycle_rhos else None
        trend_rows.append(
            {
                "feature": feature,
                "profiles_with_cycle_rho": len(cycle_rhos),
                "median_within_profile_spearman_vs_cycle": _median_or_none(cycle_rhos),
                "cycle_direction_consistency": directional,
                "profiles_with_capacity_rho": len(capacity_rhos),
                "median_within_profile_spearman_vs_capacity": _median_or_none(capacity_rhos),
                "capacity_direction_consistency": (
                    max(
                        sum(rho > 0 for rho in capacity_rhos),
                        sum(rho < 0 for rho in capacity_rhos),
                    )
                    / len(capacity_rhos)
                    if capacity_rhos
                    else None
                ),
            }
        )
    return trend_rows


def _correlation_redundancy(frame: pd.DataFrame) -> list[dict[str, Any]]:
    per_pair: dict[tuple[str, str], list[float]] = {
        pair: [] for pair in combinations(FEATURE_NAMES, 2)
    }
    for _, profile in frame.groupby("cell_id", sort=True):
        subset = profile.loc[:, FEATURE_NAMES].apply(pd.to_numeric, errors="coerce")
        correlations = subset.corr(method="spearman", min_periods=MIN_PROFILE_CYCLES_FOR_RHO)
        for left, right in per_pair:
            rho = correlations.at[left, right]
            if pd.notna(rho) and np.isfinite(rho):
                per_pair[(left, right)].append(float(rho))
    result = []
    for (left, right), values in per_pair.items():
        if len(values) < MIN_PROFILES_FOR_CORRELATION:
            continue
        median = float(np.median(values))
        if abs(median) < 0.9:
            continue
        result.append(
            {
                "feature_a": left,
                "feature_b": right,
                "median_within_profile_spearman": median,
                "profiles_with_defined_correlation": len(values),
                "direction_consistency": max(
                    sum(value > 0 for value in values),
                    sum(value < 0 for value in values),
                )
                / len(values),
            }
        )
    return sorted(
        result,
        key=lambda item: (
            -abs(item["median_within_profile_spearman"]),
            -item["profiles_with_defined_correlation"],
        ),
    )


def _feature_availability(frame: pd.DataFrame) -> list[dict[str, Any]]:
    results = []
    for feature in FEATURE_NAMES:
        finite = np.isfinite(pd.to_numeric(frame[feature], errors="coerce").to_numpy())
        per_profile = frame.assign(_available=finite).groupby("cell_id")["_available"].mean()
        results.append(
            {
                "feature": feature,
                "available_cycles": int(finite.sum()),
                "unavailable_cycles": int((~finite).sum()),
                "availability_fraction": float(finite.mean()),
                "profiles_with_any_unavailable": int((per_profile < 1).sum()),
                "minimum_profile_availability_fraction": float(per_profile.min()),
            }
        )
    return results


def _plot_feature_trajectory(
    frame: pd.DataFrame,
    feature: str,
    output_dir: Path,
) -> str:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), constrained_layout=True)
    batch_colors = plt.get_cmap("tab10")
    for batch, batch_frame in frame.groupby("batch", sort=True):
        color = batch_colors((int(batch) - 1) % 10)
        for _, profile in batch_frame.groupby("cell_id", sort=True):
            profile = profile.sort_values("cycle_index")
            values = pd.to_numeric(profile[feature], errors="coerce")
            valid = np.isfinite(values.to_numpy(dtype=np.float64))
            if not valid.any():
                continue
            axes[0].plot(
                profile.loc[valid, "cycle_index"],
                values.loc[valid],
                color=color,
                alpha=0.16,
                linewidth=0.7,
            )
            axes[1].plot(
                profile.loc[valid, "capacity_label"],
                values.loc[valid],
                color=color,
                alpha=0.16,
                linewidth=0.7,
            )
    axes[0].set_title(f"{feature} by cycle")
    axes[0].set_xlabel("Prepared cycle ordinal within profile")
    axes[0].set_ylabel("Candidate feature value")
    axes[1].set_title(f"{feature} by measured capacity label")
    axes[1].set_xlabel("Stored capacity label (unit/lineage unspecified)")
    axes[1].set_ylabel("Candidate feature value")
    handles = [
        plt.Line2D([0], [0], color=batch_colors((batch - 1) % 10), label=f"Batch {batch}")
        for batch in sorted(frame["batch"].unique())
    ]
    fig.legend(handles=handles, loc="upper center", ncol=6, frameon=False)
    path = output_dir / f"{feature}.png"
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return str(path.relative_to(REPOSITORY_ROOT)).replace("\\", "/")


def analyze_aging(
    data_root: Path = DEFAULT_DATA_ROOT,
    figure_dir: Path = DEFAULT_FIGURES,
) -> dict[str, Any]:
    frame, counts = load_candidate_frame(data_root)
    feature_rows = _feature_profile_trends(frame)
    availability = _feature_availability(frame)
    redundancy = _correlation_redundancy(frame)

    profile_capacity_summary = []
    for cell_id, profile in frame.groupby("cell_id", sort=True):
        capacities = profile["capacity_label"].astype(float)
        profile_capacity_summary.append(
            {
                "cell_id": cell_id,
                "batch": int(profile["batch"].iloc[0]),
                "cycles": len(profile),
                "first_observed_capacity": float(capacities.iloc[0]),
                "minimum_capacity": float(capacities.min()),
                "maximum_capacity": float(capacities.max()),
                "capacity_change_first_to_last": float(capacities.iloc[-1] - capacities.iloc[0]),
                "capacity_units_or_soh_status": "Capacity units and per-cell initial-capacity reference are not established; not SOH.",
            }
        )

    informative = sorted(
        (
            item
            for item in feature_rows
            if item["profiles_with_capacity_rho"] >= MIN_PROFILES_FOR_CORRELATION
        ),
        key=lambda item: abs(
            item["median_within_profile_spearman_vs_capacity"] or 0
        ),
        reverse=True,
    )[:15]
    representatives = [item["feature"] for item in informative[:3]]
    figure_dir.mkdir(parents=True, exist_ok=True)
    plots = [
        _plot_feature_trajectory(frame, feature, figure_dir)
        for feature in representatives
    ]
    batch_medians = []
    for batch, batch_frame in frame.groupby("batch", sort=True):
        batch_medians.append(
            {
                "batch": int(batch),
                "profiles": int(batch_frame["cell_id"].nunique()),
                "cycles": len(batch_frame),
                "feature_medians": {
                    feature: (
                        float(pd.to_numeric(batch_frame[feature], errors="coerce").median())
                        if pd.to_numeric(batch_frame[feature], errors="coerce").notna().any()
                        else None
                    )
                    for feature in FEATURE_NAMES
                },
            }
        )
    return {
        "analysis": "Within-profile descriptive aging analysis of the current 67 candidate features on prepared XJTU charge traces.",
        "original_benchmark_reproduction": False,
        "data": {
            **counts,
            "capacity_target_interpretation": (
                "Raw capacity_label is used as a within-profile aging proxy. "
                "Neither its local unit nor a per-cell initial-capacity denominator "
                "is established here; values are not called SOH."
            ),
            "capacity_initialization": {
                "initial_capacity_verified": False,
                "per_cell_first_observed_capacity_is_nominal_reference": False,
                "per_cell_normalization_applied": False,
                "reason": "No authoritative beginning-of-life capacity reference or target normalization lineage was available.",
            },
            "workbook_cycle_mapping_used": False,
            "profile_capacity_summaries": profile_capacity_summary,
        },
        "feature_availability": availability,
        "within_profile_trends": feature_rows,
        "potentially_informative_candidates": {
            "selection_rule": (
                "Rank by absolute median within-profile Spearman association with "
                "capacity_label among features with at least 10 profiles having "
                "defined correlations. Descriptive screening only."
            ),
            "features": informative,
            "causal_or_predictive_claim": False,
        },
        "within_profile_feature_redundancy": {
            "threshold": 0.9,
            "minimum_profiles": MIN_PROFILES_FOR_CORRELATION,
            "method": "Median Spearman correlation for each feature pair calculated separately within each profile, then summarized across profiles.",
            "pairs": redundancy,
        },
        "batch_profile_differences": {
            "batch_summaries": batch_medians,
            "interpretation": "Descriptive. Batch is confounded with protocol and cell cohort; no causal protocol effect is inferred.",
        },
        "plots": [
            {
                "path": path,
                "features": representatives,
                "description": "Per-cell feature trajectory versus cycle ordinal and stored capacity label; colors distinguish batches.",
                "normalization": "None; no unverified initial-capacity normalization was applied.",
            }
            for path in plots
        ],
        "method_limitations": [
            "Candidate segments and feature equations remain source-unverified.",
            "Cycle ordering is the prepared MAT array ordinal; this analysis does not claim correspondence to Excel workbook rows.",
            "Within-profile Spearman correlations avoid pooled between-cell correlation confounding but do not establish causality.",
            "Batch differences may reflect protocol, cohort, or other confounded variables.",
            "Capacity is not normalized to verified initial capacity; no SOH values are inferred.",
            "Potentially informative features are screening candidates, not validated predictors.",
        ],
    }


def _markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Member 4 Feature Aging Analysis",
        "",
        "## Scope and scientific status",
        "",
        "This is a descriptive analysis of candidate features extracted from the "
        "available prepared XJTU charge traces. It does not reproduce original "
        "SOHbenchmark values. No cycle-to-workbook identity mapping is assumed.",
        "",
        f"- Prepared profiles: **{result['data']['profiles']}**; cycles: "
        f"**{result['data']['prepared_cycles']}**; workbook rows, shown only "
        f"for context: **{result['data']['workbook_rows']}**.",
        "- Capacity labels are treated as raw measured-capacity proxies, not SOH: "
        "the inspected local data do not establish their unit or a per-cell "
        "beginning-of-life denominator.",
        "- No per-cell normalization was applied. A first observed capacity is "
        "not assumed to be nominal or beginning-of-life capacity.",
        "- All correlations are calculated within profiles before summarizing "
        "across profiles; pooled cross-cell correlations are not used to select "
        "aging candidates.",
        "",
        "## Feature availability",
        "",
        "| Feature | Available cycles | Unavailable cycles | Availability | Profiles with any missing values | Minimum profile availability |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for item in result["feature_availability"]:
        lines.append(
            f"| {item['feature']} | {item['available_cycles']} | "
            f"{item['unavailable_cycles']} | {item['availability_fraction']:.4f} | "
            f"{item['profiles_with_any_unavailable']} | "
            f"{item['minimum_profile_availability_fraction']:.4f} |"
        )
    lines.extend(
        [
            "",
            "Unavailable candidate values primarily arise when the current "
            "candidate phase/window is absent or cannot support its calculation. "
            "They do not necessarily indicate missing raw measurements.",
            "",
            "## Within-profile trends and capacity relationships",
            "",
            "For each feature, Spearman rho was calculated separately against "
            "prepared cycle ordinal and the stored capacity label within each "
            "profile; the table reports the median and number of profiles with "
            "a defined rho. These are associations, not causal effects.",
            "",
            "| Feature | Profiles: cycle rho | Median rho vs cycle | Cycle direction consistency | Profiles: capacity rho | Median rho vs capacity | Capacity direction consistency |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    def fmt(value: float | None) -> str:
        return "—" if value is None else f"{value:.4f}"

    for item in result["within_profile_trends"]:
        lines.append(
            f"| {item['feature']} | {item['profiles_with_cycle_rho']} | "
            f"{fmt(item['median_within_profile_spearman_vs_cycle'])} | "
            f"{fmt(item['cycle_direction_consistency'])} | "
            f"{item['profiles_with_capacity_rho']} | "
            f"{fmt(item['median_within_profile_spearman_vs_capacity'])} | "
            f"{fmt(item['capacity_direction_consistency'])} |"
        )
    lines.extend(
        [
            "",
            "### Candidate features for further investigation",
            "",
            "The following are ranked by absolute median within-profile "
            "capacity-label rho and require further validation; they are not "
            "endorsed predictors.",
            "",
            "| Feature | Median within-profile rho vs capacity | Profiles |",
            "|---|---:|---:|",
        ]
    )
    for item in result["potentially_informative_candidates"]["features"]:
        lines.append(
            f"| {item['feature']} | "
            f"{fmt(item['median_within_profile_spearman_vs_capacity'])} | "
            f"{item['profiles_with_capacity_rho']} |"
        )
    lines.extend(
        [
            "",
            "## Batch/profile distribution differences",
            "",
            "Feature medians by batch are stored in the JSON summary. Batch "
            "differences are descriptive and may combine protocol effects with "
            "cell-cohort and other differences.",
            "",
            "| Batch | Profiles | Cycles | Capacity-label range across profiles (min of per-cell minima to max of maxima) |",
            "|---:|---:|---:|---:|",
        ]
    )
    per_batch_capacity = {}
    for cell in result["data"]["profile_capacity_summaries"]:
        per_batch_capacity.setdefault(cell["batch"], []).append(cell)
    for batch in result["batch_profile_differences"]["batch_summaries"]:
        cells = per_batch_capacity[batch["batch"]]
        low = min(cell["minimum_capacity"] for cell in cells)
        high = max(cell["maximum_capacity"] for cell in cells)
        lines.append(
            f"| {batch['batch']} | {batch['profiles']} | {batch['cycles']} | "
            f"{low:.5g} to {high:.5g} |"
        )
    lines.extend(
        [
            "",
            "## Feature redundancy",
            "",
            "Pairs are flagged when the median within-profile Spearman rho has "
            "absolute value at least 0.9 across at least 10 profiles. This "
            "screens redundant candidate outputs; it does not identify a causal "
            "mechanism.",
            "",
            "| Feature A | Feature B | Median within-profile rho | Profiles | Direction consistency |",
            "|---|---|---:|---:|---:|",
        ]
    )
    for pair in result["within_profile_feature_redundancy"]["pairs"]:
        lines.append(
            f"| {pair['feature_a']} | {pair['feature_b']} | "
            f"{pair['median_within_profile_spearman']:.4f} | "
            f"{pair['profiles_with_defined_correlation']} | "
            f"{pair['direction_consistency']:.4f} |"
        )
    lines.extend(["", "## Representative trajectories", ""])
    for plot in result["plots"]:
        relative = Path(plot["path"]).relative_to("reports/member4").as_posix()
        lines.extend(
            [
                f"### {', '.join(plot['features'])}",
                "",
                f"![{', '.join(plot['features'])} trajectory]({relative})",
                "",
                "Two panels show the candidate feature against per-profile cycle "
                "ordinal and against the stored capacity label. Lines are "
                "un-normalized, and color denotes batch.",
                "",
            ]
        )
    lines.extend(
        [
            "## Interpretation limits",
            "",
            "- The capacity field is not verified SOH; target units and initial "
            "capacity are not established. No per-cell capacity normalization "
            "or SOH conversion was performed.",
            "- Correlations, direction consistency, feature rankings, and "
            "between-batch differences are exploratory and do not prove "
            "causality or predictive value.",
            "- Prepared-array cycle ordinal is not asserted to identify the "
            "corresponding workbook row.",
            "- Candidate formulas and phase windows remain unverified against "
            "the original feature generator.",
            "",
            "## Reproducibility",
            "",
            "From the repository root:",
            "",
            "```powershell",
            ".\\.venv\\Scripts\\python.exe -m scripts.member4_xjtu.aging_analysis",
            "```",
            "",
            "The script writes this report, its JSON summary, and trajectory "
            "plots under `reports/member4/`.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    result = analyze_aging()
    DEFAULT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_SUMMARY.write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    DEFAULT_REPORT.write_text(_markdown(result), encoding="utf-8")
    print(
        f"Wrote {DEFAULT_REPORT} and {DEFAULT_SUMMARY}: "
        f"{result['data']['prepared_cycles']} cycles, {len(FEATURE_NAMES)} features, "
        f"{len(result['plots'])} plots."
    )

if __name__ == "__main__":
    main()
