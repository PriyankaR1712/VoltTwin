import numpy as np
import pytest
from fastapi import HTTPException

from backend import formula_explorer_api
from scripts.member4_xjtu.feature_definitions import FEATURE_NAMES
from scripts.member4_xjtu.models import CycleTrace


def _trace() -> CycleTrace:
    return CycleTrace(
        batch=1,
        profile="Sheet1",
        cycle_index=1,
        time_min=np.array([0.0, 1.0, 2.0]),
        voltage_v=np.array([3.0, 4.0, 5.0]),
        current_a=np.array([2.0, 2.0, 2.0]),
        temperature_c=np.array([20.0, 21.0, 22.0]),
        capacity_label=1.8,
    )


def _group_trace() -> CycleTrace:
    time = np.linspace(0.0, 12.7, 128)
    voltage = np.concatenate((np.linspace(3.5, 4.2, 86), np.full(42, 4.2)))
    current = np.full(128, 4.0)
    current[90:] = np.linspace(3.8, 0.1, 38)
    return CycleTrace(
        batch=1,
        profile="Sheet1",
        cycle_index=1,
        time_min=time,
        voltage_v=voltage,
        current_a=current,
        temperature_c=25.0 + 0.1 * time,
        capacity_label=1.8,
    )


def test_formula_definitions_preserve_all_features_and_unverified_status():
    response = formula_explorer_api.get_formula_features()

    features = response["features"]
    assert response["count"] == 67
    assert response["source_verified_count"] == 0
    assert tuple(feature["name"] for feature in features) == FEATURE_NAMES
    assert {
        group: sum(feature["group"] == group for feature in features)
        for group in ("CC", "dV", "CV", "dI", "Charge")
    } == {"CC": 13, "dV": 13, "CV": 13, "dI": 13, "Charge": 15}
    assert all(feature["status"] != "source_verified" for feature in features)
    assert all(
        feature["original_benchmark_formula"]
        == "Unavailable — original formula not verified."
        for feature in features
    )
    assert all(feature["candidate_equation"] for feature in features)
    assert all(feature["variables"] for feature in features)

    entropy_features = [
        feature for feature in features if feature["name"].endswith("_entropy")
    ]
    assert len(entropy_features) == 4
    assert all(
        feature["status"] == "original_formula_unknown"
        for feature in entropy_features
    )
    assert all(
        feature["status"] == "candidate_unverified"
        for feature in features
        if not feature["name"].endswith("_entropy")
    )

    features_by_name = {feature["name"]: feature for feature in features}
    assert features_by_name["dV_dV_devide_dt"]["input_units"] == {
        "voltage": "V",
        "time": "min",
    }
    assert features_by_name["dI_dI_devide_dt"]["input_units"] == {
        "current": "A",
        "time": "min",
    }
    for name in ("CC_CCCT", "CV_CVCT"):
        duration = features_by_name[name]
        assert "single contiguous interval" in duration["candidate_equation"]
        assert "unavailable if disjoint" in duration["candidate_equation"]
        assert [variable["symbol"] for variable in duration["variables"]] == [
            "t_start",
            "t_end",
        ]


def test_candidate_calculation_returns_raw_trace_segments_and_values(monkeypatch):
    trace = _trace()
    monkeypatch.setattr(
        formula_explorer_api,
        "_load_batch",
        lambda batch: ([[trace]], {}),
    )

    response = formula_explorer_api.calculate_candidate_features(
        batch=1,
        profile="Sheet1",
        cycle=1,
        feature_name="Charge_energy",
    )

    assert response["is_candidate_calculation"] is True
    assert response["values_are_original_benchmark_values"] is False
    assert response["feature_values"]["Charge_energy"] == pytest.approx(16 / 60)
    energy_detail = response["calculation_details"]["Charge_energy"]
    assert energy_detail["operation"] == "trapezoidal_time_integration"
    assert energy_detail["candidate_result"] == pytest.approx(16 / 60)
    assert energy_detail["integration_by_interval"][0]["sample_count"] == 3
    assert energy_detail["integration_by_interval"][0]["panel_count"] == 2
    panel_details = energy_detail["integration_by_interval"][0]["trapezoid_panels"]
    assert len(panel_details) == 2
    assert sum(panel["panel_integral"] for panel in panel_details) == pytest.approx(16)
    assert response["calculation_detail"]["candidate_result"] == pytest.approx(
        response["feature_values"]["Charge_energy"]
    )
    assert response["values_are_original_benchmark_values"] is False
    assert response["trace"]["time_min"] == [0.0, 1.0, 2.0]
    assert response["raw_sampling"]["is_uniform"] is True
    assert response["raw_sample_indices_by_group"]["Charge"] == [0, 1, 2]
    assert response["segments"]["Charge"]["intervals"] == [
        {"start_min": 0.0, "end_min": 2.0}
    ]


@pytest.mark.parametrize(
    ("feature_name", "group"),
    [
        ("CC_energy", "CC"),
        ("dV_dV_devide_dt", "dV"),
        ("CV_CVCT", "CV"),
        ("dI_dI_devide_dt", "dI"),
        ("Charge_energy", "Charge"),
    ],
)
def test_candidate_calculation_returns_selected_group_data_and_details(
    monkeypatch, feature_name, group
):
    trace = _group_trace()
    monkeypatch.setattr(
        formula_explorer_api,
        "_load_batch",
        lambda batch: ([[trace]], {}),
    )

    response = formula_explorer_api.calculate_candidate_features(
        batch=1,
        profile="Sheet1",
        cycle=1,
        feature_name=feature_name,
    )

    assert response["batch"] == trace.batch
    assert response["profile"] == trace.profile
    assert response["cycle"] == trace.cycle_index
    assert response["trace"]["time_min"] == trace.time_min.tolist()
    assert set(response["feature_values"]) == set(FEATURE_NAMES)
    assert response["segments"][group]["intervals"]
    assert response["raw_sample_indices_by_group"][group]
    detail = response["calculation_detail"]
    assert detail["feature"]["name"] == feature_name
    assert detail["feature"]["group"] == group
    assert detail["candidate_result"] == response["feature_values"][feature_name]
    assert detail["intermediate_calculation"]["operation"]


def test_candidate_calculation_reports_unavailable_feature_without_fabrication(
    monkeypatch,
):
    trace = CycleTrace(
        batch=1,
        profile="Sheet1",
        cycle_index=1,
        time_min=np.array([0.0, 1.0, 2.0]),
        voltage_v=np.array([3.0, 3.4, 3.8]),
        current_a=np.array([2.0, 2.0, 2.0]),
        temperature_c=np.array([20.0, 21.0, 22.0]),
        capacity_label=1.8,
    )
    monkeypatch.setattr(
        formula_explorer_api,
        "_load_batch",
        lambda batch: ([[trace]], {}),
    )

    response = formula_explorer_api.calculate_candidate_features(
        batch=1,
        profile="Sheet1",
        cycle=1,
        feature_name="CV_energy",
    )

    assert response["feature_values"]["CV_energy"] is None
    assert response["calculation_detail"]["candidate_result"] is None
    assert response["calculation_detail"]["intermediate_calculation"] is None
    assert response["segments"]["CV"]["intervals"] == []


def test_candidate_calculation_rejects_unknown_feature(monkeypatch):
    monkeypatch.setattr(
        formula_explorer_api,
        "_load_batch",
        lambda batch: ([[_trace()]], {}),
    )

    with pytest.raises(HTTPException) as error:
        formula_explorer_api.calculate_candidate_features(
            batch=1,
            profile="Sheet1",
            cycle=1,
            feature_name="not_a_feature",
        )

    assert error.value.status_code == 422
    assert "Unknown feature name" in str(error.value.detail)


@pytest.mark.parametrize(
    "endpoint",
    ["profiles", "calculate"],
)
def test_missing_dataset_is_reported_as_service_unavailable(monkeypatch, endpoint):
    def missing_batch(batch):
        raise FileNotFoundError("missing test dataset")

    monkeypatch.setattr(formula_explorer_api, "_load_batch", missing_batch)

    with pytest.raises(HTTPException) as error:
        if endpoint == "profiles":
            formula_explorer_api.get_batch_profiles(batch=1)
        else:
            formula_explorer_api.calculate_candidate_features(
                batch=1,
                profile="Sheet1",
                cycle=1,
                feature_name="Charge_energy",
            )

    assert error.value.status_code == 503


@pytest.mark.parametrize(
    ("profile", "cycle", "message"),
    [
        ("Sheet2", 1, "Sheet2 is not available"),
        ("Sheet1", 2, "Cycle 2 is not available"),
    ],
)
def test_candidate_calculation_rejects_missing_profile_or_cycle(
    monkeypatch, profile, cycle, message
):
    monkeypatch.setattr(
        formula_explorer_api,
        "_load_batch",
        lambda batch: ([[_trace()]], {}),
    )

    with pytest.raises(HTTPException, match=message):
        formula_explorer_api.calculate_candidate_features(
            batch=1,
            profile=profile,
            cycle=cycle,
            feature_name="Charge_energy",
        )
