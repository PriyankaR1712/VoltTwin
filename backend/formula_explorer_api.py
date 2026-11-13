from __future__ import annotations

from functools import lru_cache
from typing import Any

import numpy as np
from fastapi import APIRouter, HTTPException, Path as PathParam, Query

from scripts.member4_xjtu.extractor import extract_cycle_with_details
from scripts.member4_xjtu.feature_definitions import FEATURE_NAMES, feature_definitions
from scripts.member4_xjtu.loader import load_batch
from scripts.member4_xjtu.models import CycleTrace

router = APIRouter(prefix="/formula-explorer", tags=["Formula Explorer"])


@lru_cache(maxsize=1)
def _load_batch(batch: int) -> tuple[list[list[CycleTrace]], dict[str, Any]]:
    return load_batch(batch)


def _calculation_steps(name: str) -> list[str]:
    if name.endswith("_energy"):
        return [
            "Select the candidate interval for this feature group.",
            "Multiply voltage by current at the recorded timestamps.",
            "Integrate power over time with trapezoidal integration and convert minutes to hours.",
        ]
    if name.endswith("_Q"):
        return [
            "Select the candidate interval for this feature group.",
            "Integrate current over the recorded timestamps with trapezoidal integration.",
            "Convert minutes to hours to express the result in ampere-hours.",
        ]
    if name.endswith("_t_mean"):
        return [
            "Select the candidate interval for this feature group.",
            "Interpolate elapsed time onto a 257-point uniform-time grid.",
            "Take the arithmetic mean of elapsed time from the interval start.",
        ]
    if name.endswith(("_CCCT", "_CVCT")):
        return [
            "Select the candidate phase interval.",
            "Subtract its start time from its end time.",
            "The original workbook's phase boundary convention is unknown.",
        ]
    if name.endswith("_devide_dt"):
        signal = "voltage" if name.startswith("dV_") else "current"
        return [
            "Select the candidate threshold window.",
            f"Subtract the {signal} value at the start from the value at the end.",
            "Divide that difference by the candidate interval duration.",
        ]
    if name.endswith("_entropy"):
        return [
            "Interpolate the selected signal onto 257 uniform-time points per candidate interval.",
            "Count interpolated samples in 16 equal-width histogram bins and convert counts to probabilities.",
            "Compute Shannon entropy with the natural logarithm; this is a diagnostic proxy only.",
        ]

    statistic = name.rsplit("_", maxsplit=1)[-1]
    return [
        "Select the signal and candidate interval shown.",
        "Interpolate the signal onto a 257-point uniform-time grid.",
        {
            "mean": "Compute the arithmetic mean.",
            "std": "Compute the population standard deviation (ddof=0).",
            "skewness": "Compute the biased third standardized central moment.",
            "kurtosis": "Compute the Pearson fourth standardized central moment (not excess kurtosis).",
        }[statistic],
    ]


def _status(definition: Any) -> str:
    if definition.evidence_class == "unknown_original_definition":
        return "original_formula_unknown"
    return "candidate_unverified"


def _formula_notation(name: str) -> str:
    if name.endswith("_energy"):
        return "E_candidate = (1/60) Σᵢ [(VᵢIᵢ + Vᵢ₊₁Iᵢ₊₁)/2] Δtᵢ"
    if name.endswith("_Q"):
        return "Q_candidate = (1/60) Σᵢ [(Iᵢ + Iᵢ₊₁)/2] Δtᵢ"
    if name.endswith("_t_mean"):
        return "t̄_candidate = (1/N) Σⱼ (tⱼ − t₀), using 257-point grids per interval"
    if name.endswith(("_CCCT", "_CVCT")):
        return (
            "Duration_candidate = t_end − t_start "
            "(single contiguous interval; unavailable if disjoint)"
        )
    if name.endswith("_devide_dt"):
        signal = "V" if name.startswith("dV_") else "I"
        return (
            f"Rate_candidate = ({signal}_end − {signal}_start) "
            "/ (t_end − t_start)"
        )
    if name.endswith("_entropy"):
        return "H_diagnostic = −Σᵦ pᵦ ln(pᵦ), using a 16-bin histogram"

    suffixes = name.rsplit("_", maxsplit=1)
    if len(suffixes) == 2 and suffixes[1] in {
        "mean",
        "std",
        "skewness",
        "kurtosis",
    }:
        statistic = suffixes[1]
        if statistic == "mean":
            return "μₓ = (1/N) Σᵢ xᵢ"
        if statistic == "std":
            return "σₓ = √[(1/N) Σᵢ (xᵢ − μₓ)²], population standard deviation"
        if statistic == "skewness":
            return "γ₁ = [(1/N) Σᵢ (xᵢ − μₓ)³] / σₓ³"
        return "β₂ = [(1/N) Σᵢ (xᵢ − μₓ)⁴] / σₓ⁴, Pearson kurtosis"
    return "Candidate equation unavailable."


def _implementation_description(name: str) -> str:
    if name.endswith("_energy"):
        return (
            "The existing extractor multiplies interpolated voltage and current "
            "at interval sample times, applies trapezoidal integration over native "
            "timestamps plus interpolated boundaries, then divides minutes by 60."
        )
    if name.endswith("_Q"):
        return (
            "The existing extractor applies trapezoidal integration to current over "
            "native timestamps plus interpolated boundaries, then divides minutes by 60."
        )
    if name.endswith("_t_mean"):
        return (
            "The existing extractor interpolates elapsed time onto 257 uniform points "
            "per selected interval and takes their arithmetic mean."
        )
    if name.endswith(("_CCCT", "_CVCT")):
        return (
            "The existing extractor sums selected interval durations; these columns "
            "are returned only for a single contiguous interval."
        )
    if name.endswith("_devide_dt"):
        return (
            "The existing extractor linearly interpolates the signal at candidate "
            "window endpoints and divides the endpoint difference by interval duration."
        )
    if name.endswith("_entropy"):
        return (
            "The existing extractor reports a diagnostic Shannon histogram proxy "
            "using a 257-point uniform-time grid per interval, 16 equal-width bins, "
            "and natural logarithms; the original entropy definition is unknown."
        )
    return (
        "The existing extractor linearly interpolates the selected channel to a "
        "257-point uniform-time grid, then calculates the stated population-moment "
        "statistic. Skewness is the biased standardized third central moment; "
        "kurtosis is Pearson, not excess."
    )


def _input_units(name: str, signal: str) -> dict[str, str]:
    units = {"time": "min", "voltage": "V", "current": "A", "temperature": "°C"}
    if name.endswith("_energy"):
        return {"voltage": "V", "current": "A", "time": "min"}
    if name.endswith("_Q"):
        return {"current": "A", "time": "min"}
    if name.endswith(("_CCCT", "_CVCT", "_t_mean", "_devide_dt")):
        if name.endswith("_devide_dt"):
            signal_unit = "V" if name.startswith("dV_") else "A"
            signal_name = "voltage" if name.startswith("dV_") else "current"
            return {signal_name: signal_unit, "time": "min"}
        return {"time": "min"}
    if name.endswith("_entropy"):
        if "voltage" in signal:
            return {"voltage": "V"}
        if "current" in signal:
            return {"current": "A"}
        return {}
    if "voltage" in signal:
        return {"selected signal": units["voltage"]}
    if "current" in signal:
        return {"selected signal": units["current"]}
    if "temperature" in signal:
        return {"selected signal": units["temperature"]}
    return {}


def _variables(name: str, signal: str) -> list[dict[str, str]]:
    if name.endswith("_energy"):
        return [
            {"symbol": "V", "meaning": "Voltage at the sampled time", "unit": "V"},
            {"symbol": "I", "meaning": "Current at the sampled time", "unit": "A"},
            {"symbol": "t", "meaning": "Elapsed time", "unit": "min"},
            {"symbol": "Δtᵢ", "meaning": "Time difference for trapezoid panel i", "unit": "min"},
            {"symbol": "60", "meaning": "Minutes per hour conversion", "unit": "min/h"},
        ]
    if name.endswith("_Q"):
        return [
            {"symbol": "I", "meaning": "Current at the sampled time", "unit": "A"},
            {"symbol": "t", "meaning": "Elapsed time", "unit": "min"},
            {"symbol": "Δtᵢ", "meaning": "Time difference for trapezoid panel i", "unit": "min"},
            {"symbol": "60", "meaning": "Minutes per hour conversion", "unit": "min/h"},
        ]
    if name.endswith("_t_mean"):
        return [
            {"symbol": "tⱼ", "meaning": "Uniform-grid time sample j", "unit": "min"},
            {"symbol": "t₀", "meaning": "Start time of the selected interval", "unit": "min"},
            {"symbol": "N", "meaning": "Grid point count (257 per interval)", "unit": "samples"},
        ]
    if name.endswith(("_CCCT", "_CVCT")):
        return [
            {"symbol": "t_start", "meaning": "Start time of the candidate interval", "unit": "min"},
            {"symbol": "t_end", "meaning": "End time of the candidate interval", "unit": "min"},
        ]
    if name.endswith("_devide_dt"):
        signal_symbol = "V" if name.startswith("dV_") else "I"
        signal_unit = "V" if signal_symbol == "V" else "A"
        return [
            {"symbol": signal_symbol, "meaning": f"{signal} signal", "unit": signal_unit},
            {"symbol": "t_start / t_end", "meaning": "Candidate window boundary times", "unit": "min"},
            {"symbol": "Δsignal", "meaning": "End value minus start value", "unit": signal_unit},
            {"symbol": "Δt", "meaning": "Candidate window duration", "unit": "min"},
        ]
    if name.endswith("_entropy"):
        signal_unit = (
            "V" if "voltage" in signal else "A" if "current" in signal else "not located"
        )
        return [
            {
                "symbol": "x",
                "meaning": f"{signal} samples in the candidate interval",
                "unit": signal_unit,
            },
            {"symbol": "b", "meaning": "Histogram bin index", "unit": "dimensionless"},
            {"symbol": "pᵦ", "meaning": "Fraction of samples in bin b", "unit": "dimensionless"},
            {"symbol": "ln", "meaning": "Natural logarithm in diagnostic proxy", "unit": "dimensionless"},
        ]

    channel = name.split("_")[1][0]
    signal_unit = {
        "V": "V",
        "C": "A",
        "T": "°C",
    }.get(channel, "not located")
    variables = [
        {"symbol": "xᵢ", "meaning": f"{signal} sample i", "unit": signal_unit},
        {"symbol": "N", "meaning": "Uniform-time grid sample count", "unit": "samples"},
        {"symbol": "μₓ", "meaning": "Arithmetic mean of x", "unit": signal_unit},
    ]
    if name.endswith("_std"):
        variables.append(
            {"symbol": "σₓ", "meaning": "Population standard deviation of x", "unit": signal_unit}
        )
    elif name.endswith("_skewness"):
        variables.extend(
            [
                {"symbol": "m₃", "meaning": "Third central moment of x", "unit": f"{signal_unit}³"},
                {"symbol": "σₓ", "meaning": "Population standard deviation of x", "unit": signal_unit},
            ]
        )
    elif name.endswith("_kurtosis"):
        variables.extend(
            [
                {"symbol": "m₄", "meaning": "Fourth central moment of x", "unit": f"{signal_unit}⁴"},
                {"symbol": "σₓ", "meaning": "Population standard deviation of x", "unit": signal_unit},
            ]
        )
    return variables


def _category_description(group: str) -> str:
    return {
        "CC": "Candidate constant-current-like charging interval; original Excel boundaries are not verified.",
        "dV": "Candidate rising voltage window within CC; exact source interval is unknown.",
        "CV": "Candidate constant-voltage-like interval; original Excel boundaries are not verified.",
        "dI": "Candidate falling-current window within CV; exact source interval is unknown.",
        "Charge": "Entire stored charging trace in the candidate extractor; original workbook limits are unknown.",
    }[group]


def _research_evidence(name: str) -> dict[str, str]:
    if name.endswith("_entropy"):
        summary = (
            "Original entropy signal, estimator, binning, weighting, and logarithm "
            "base are not located. The current histogram is diagnostic only."
        )
    else:
        summary = (
            "The research report found no original generator or source formula for "
            "this workbook column. Any displayed equation is the candidate "
            "implementation, not a verified benchmark definition."
        )
    if name.startswith(("CC_", "CV_")):
        summary += (
            " The XJTU author helper documents some CC/CV sample selectors, but "
            "does not establish this workbook's feature formula or boundaries."
        )
    return {
        "report": "reports/member4_formula_research.md",
        "summary": summary,
    }


def _feature_provenance(definition: Any, order: int) -> dict[str, Any]:
    item = definition.as_dict()
    status = _status(definition)
    item.update(
        {
            "order": order,
            "status": status,
            "status_label": {
                "source_verified": "Source Verified",
                "candidate_unverified": "Candidate / Unverified",
                "original_formula_unknown": "Original Formula Unknown",
            }[status],
            "original_benchmark_formula": (
                "Unavailable — original formula not verified."
            ),
            "candidate_formula": definition.candidate_formula,
            "mathematical_interpretation": definition.candidate_formula,
            "candidate_equation": _formula_notation(definition.name),
            "implementation_used": _implementation_description(definition.name),
            "input_units": _input_units(definition.name, definition.signal),
            "output_units": definition.unit,
            "variables": _variables(definition.name, definition.signal),
            "category_description": _category_description(definition.group),
            "research_evidence": _research_evidence(definition.name),
            "calculation_steps": _calculation_steps(definition.name),
        }
    )
    return item


@router.get("/features")
def get_formula_features() -> dict[str, Any]:
    """Return candidate interpretations in the canonical 67-feature order."""
    definitions = feature_definitions()
    features = [
        _feature_provenance(definition, order)
        for order, definition in enumerate(definitions, start=1)
    ]

    return {
        "features": features,
        "count": len(features),
        "source_verified_count": 0,
        "notice": (
            "Original XJTU workbook formulas have not been verified. "
            "Candidate interpretations are not author-confirmed formulas."
        ),
    }


@router.get("/batches/{batch}/profiles")
def get_batch_profiles(batch: int = PathParam(ge=1, le=6)) -> dict[str, Any]:
    try:
        profiles, _ = _load_batch(batch)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail="The XJTU raw data or feature workbook is unavailable.",
        ) from exc

    return {
        "batch": batch,
        "profiles": [
            {"name": f"Sheet{index}", "cycle_count": len(profile)}
            for index, profile in enumerate(profiles, start=1)
        ],
    }


@router.get("/calculate")
def calculate_candidate_features(
    batch: int = Query(ge=1, le=6),
    profile: str = Query(pattern=r"^Sheet[1-9][0-9]*$"),
    cycle: int = Query(ge=1),
    feature_name: str = Query(default=FEATURE_NAMES[0]),
) -> dict[str, Any]:
    if feature_name not in FEATURE_NAMES:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown feature name: {feature_name}.",
        )

    try:
        profiles, _ = _load_batch(batch)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail="The XJTU raw data or feature workbook is unavailable.",
        ) from exc

    profile_number = int(profile.removeprefix("Sheet"))
    if profile_number > len(profiles):
        raise HTTPException(
            status_code=404,
            detail=f"{profile} is not available in batch {batch}.",
        )

    cycles = profiles[profile_number - 1]
    if cycle > len(cycles):
        raise HTTPException(
            status_code=404,
            detail=f"Cycle {cycle} is not available in {profile} of batch {batch}.",
        )

    trace = cycles[cycle - 1]
    values, segments, calculations = extract_cycle_with_details(trace)
    feature_values = {
        name: None if value is None else float(value)
        for name, value in values.items()
    }
    definitions = feature_definitions()
    definition = next(
        item for item in definitions if item.name == feature_name
    )
    calculation_detail = calculations.get(feature_name)
    sample_indices_by_group = {
        group: [
            int(index)
            for index in segment.selected_mask.nonzero()[0].tolist()
        ]
        for group, segment in segments.items()
    }
    delta_time = np.diff(trace.time_min)
    return {
        "batch": batch,
        "profile": profile,
        "cycle": cycle,
        "capacity_label": trace.capacity_label,
        "is_candidate_calculation": True,
        "values_are_original_benchmark_values": False,
        "trace": {
            "time_min": trace.time_min.tolist(),
            "voltage_v": trace.voltage_v.tolist(),
            "current_a": trace.current_a.tolist(),
            "temperature_c": trace.temperature_c.tolist(),
        },
        "segments": {
            name: {
                "selection_method": segment.selection_method,
                "evidence": segment.evidence,
                "note": segment.note,
                "intervals": [
                    {
                        "start_min": interval.start_min,
                        "end_min": interval.end_min,
                    }
                    for interval in segment.intervals
                ],
            }
            for name, segment in segments.items()
        },
        "feature_values": feature_values,
        "calculation_detail": {
            "feature": _feature_provenance(
                definition,
                FEATURE_NAMES.index(feature_name) + 1,
            ),
            "intermediate_calculation": calculation_detail,
            "candidate_result": feature_values[feature_name],
        },
        "calculation_details": calculations,
        "raw_sample_indices_by_group": sample_indices_by_group,
        "raw_sample_delta_time_min": [float(value) for value in delta_time.tolist()],
        "raw_sampling": {
            "sample_count": int(len(trace.time_min)),
            "minimum_delta_time_min": float(np.min(delta_time)),
            "maximum_delta_time_min": float(np.max(delta_time)),
            "median_delta_time_min": float(np.median(delta_time)),
            "is_uniform": bool(
                np.allclose(
                    delta_time,
                    np.median(delta_time),
                    rtol=1e-6,
                    atol=1e-9,
                )
            ),
        },
        "notice": (
            "Values are produced by the Member 4 candidate extractor from the selected "
            "raw trace. They are not verified original workbook feature values."
        ),
    }
