from __future__ import annotations

from dataclasses import asdict, dataclass


GROUPS = ("CC", "dV", "CV", "dI", "Charge")
STATISTICS = ("mean", "std", "skewness", "kurtosis")
CHANNELS = {
    "CC": (("V", "voltage"), ("T", "temperature")),
    "dV": (("V", "voltage"), ("T", "temperature")),
    "CV": (("C", "current"), ("T", "temperature")),
    "dI": (("C", "current"), ("T", "temperature")),
    "Charge": (("V", "voltage"), ("C", "current"), ("T", "temperature")),
}


@dataclass(frozen=True)
class FeatureDefinition:
    name: str
    group: str
    signal: str
    segment: str
    candidate_formula: str
    unit: str
    evidence_class: str
    formula_status: str
    assumptions: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


def _feature_names_for_group(group: str) -> list[str]:
    names = [f"{group}_energy", f"{group}_Q", f"{group}_t_mean"]
    for statistic in STATISTICS:
        channels = CHANNELS[group]
        if group == "Charge" and statistic != "mean":
            channels = (("C", "current"), ("V", "voltage"), ("T", "temperature"))
        for suffix, _ in channels:
            names.append(f"{group}_{suffix}_{statistic}")
    if group == "CC":
        names.extend(("CC_CCCT", "CC_entropy"))
    elif group == "dV":
        names.extend(("dV_dV_devide_dt", "dV_entropy"))
    elif group == "CV":
        names.extend(("CV_CVCT", "CV_entropy"))
    elif group == "dI":
        names.extend(("dI_dI_devide_dt", "dI_entropy"))
    return names


FEATURE_NAMES = tuple(
    name for group in GROUPS for name in _feature_names_for_group(group)
)
if len(FEATURE_NAMES) != 67 or len(set(FEATURE_NAMES)) != 67:
    raise RuntimeError("The Member 4 feature schema must contain 67 unique names.")


def feature_definitions() -> list[FeatureDefinition]:
    definitions: list[FeatureDefinition] = []
    for group in GROUPS:
        segment = {
            "CC": "constant-current-like charge candidate",
            "dV": "candidate rising 3.9-4.0 V window within CC",
            "CV": "constant-voltage-like charge candidate",
            "dI": "candidate falling 1.0-0.9 A window within CV",
            "Charge": "complete stored charge trace",
        }[group]
        for name in _feature_names_for_group(group):
            suffix = name[len(group) + 1 :]
            evidence_class = "candidate_approximation"
            formula_status = "Original formula implementation not located; candidate approximation only."
            assumptions = "Workbook formula and exact segment convention remain unverified."
            if suffix == "energy":
                signal = "voltage and current"
                formula = "Trapezoidal integral of V(t)*I(t), with minutes converted to hours."
                unit = "Wh"
                evidence_class = "standard_physical_candidate"
                assumptions += " Current sign, integration convention, and interval boundaries are not source-confirmed."
            elif suffix == "Q":
                signal = "current and time"
                formula = "Trapezoidal integral of I(t), with minutes converted to hours."
                unit = "Ah"
                evidence_class = "standard_physical_candidate"
                assumptions += " Current sign, integration convention, and interval boundaries are not source-confirmed."
            elif suffix == "t_mean":
                signal = "elapsed time"
                formula = "Arithmetic mean of elapsed time on a 257-point uniform-time interpolation grid."
                unit = "min"
                assumptions += " Grid and time origin are candidate conventions."
            elif suffix in ("CCCT", "CVCT"):
                signal = "time"
                formula = "Candidate interval end minus start."
                unit = "min"
                evidence_class = "name_supported_candidate"
                assumptions += " Exact phase selector and treatment of gaps are not source-confirmed."
            elif suffix in ("dV_devide_dt", "dI_devide_dt"):
                signal = "voltage and time" if suffix.startswith("dV") else "current and time"
                formula = "Endpoint signal difference divided by candidate interval duration."
                unit = "V/min" if suffix.startswith("dV") else "A/min"
                evidence_class = "name_supported_candidate"
                assumptions += " Derivative estimator and candidate window boundaries are not source-confirmed."
            elif suffix == "entropy":
                signal = "voltage proxy" if group in ("CC", "dV") else "current proxy"
                formula = "Diagnostic proxy: Shannon entropy in nats of a 16-bin equal-width histogram."
                unit = "nats"
                evidence_class = "unknown_original_definition"
                formula_status = "Original formula unknown; histogram proxy is diagnostic only."
                assumptions = "Original entropy signal, estimator, binning, and logarithm base were not located."
            else:
                suffix_code, statistic = suffix.split("_", maxsplit=1)
                signal = {
                    "V": "voltage",
                    "C": "current",
                    "T": "temperature",
                }[suffix_code]
                unit = {
                    "mean": {"V": "V", "C": "A", "T": "degC"},
                    "std": {"V": "V", "C": "A", "T": "degC"},
                    "skewness": {"V": "dimensionless", "C": "dimensionless", "T": "dimensionless"},
                    "kurtosis": {"V": "dimensionless", "C": "dimensionless", "T": "dimensionless"},
                }[statistic][suffix_code]
                formula = {
                    "mean": f"Arithmetic mean of {signal} on a 257-point uniform-time interpolation grid.",
                    "std": f"Population standard deviation (ddof=0) of {signal} on that grid.",
                    "skewness": f"Biased third standardized central moment of {signal}.",
                    "kurtosis": f"Pearson fourth standardized central moment of {signal}.",
                }[statistic]
                assumptions += " Statistical weighting and sample/bias/excess conventions are not source-confirmed."
            definitions.append(
                FeatureDefinition(
                    name=name,
                    group=group,
                    signal=signal,
                    segment=segment,
                    candidate_formula=formula,
                    unit=unit,
                    evidence_class=evidence_class,
                    formula_status=formula_status,
                    assumptions=assumptions,
                )
            )
    return definitions
