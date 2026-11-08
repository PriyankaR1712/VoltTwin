"""
VoltTwin Feature Metadata API
Member 4 - feature metadata only.

Include this router in the central backend/main.py:
    from features_api import router as features_router
    app.include_router(features_router)

Adjust the import path if this module is placed inside a package.
"""
import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["Feature Metadata"])

# Expected layout:
# VoltTwin/
#   frontend/src/data/feature_metadata.json
#   backend/features_api.py
# Resolve from this file's location (backend/) to the repository root.
REPO_ROOT = Path(__file__).resolve().parent.parent
METADATA_PATH = REPO_ROOT / "frontend" / "src" / "data" / "feature_metadata.json"


def _load_features() -> list[dict[str, Any]]:
    try:
        with METADATA_PATH.open("r", encoding="utf-8-sig") as file:
            data = json.load(file)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Feature metadata file not found: {METADATA_PATH}",
        ) from exc
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=500,
            detail="Feature metadata JSON is invalid.",
        ) from exc

    if not isinstance(data, list):
        raise HTTPException(
            status_code=500,
            detail="Feature metadata must be a JSON array.",
        )
    return data


@router.get("/features")
def get_features() -> list[dict[str, Any]]:
    """Return all feature metadata in the original JSON/CNN order."""
    return _load_features()


@router.get("/features/groups")
def get_feature_groups() -> list[str]:
    """Return unique group names in their first-seen order."""
    features = _load_features()
    groups: list[str] = []
    seen: set[str] = set()

    for feature in features:
        group = feature.get("group")
        if isinstance(group, str) and group not in seen:
            seen.add(group)
            groups.append(group)

    return groups


@router.get("/features/{feature_id}")
def get_feature(feature_id: str) -> dict[str, Any]:
    """Return metadata for one feature ID."""
    for feature in _load_features():
        if feature.get("feature_id") == feature_id:
            return feature

    raise HTTPException(status_code=404, detail=f"Feature '{feature_id}' not found.")
