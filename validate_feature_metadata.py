
import json
from pathlib import Path
from collections import Counter

# Project root
ROOT = Path(__file__).resolve().parent

# Actual Feature Explorer metadata
METADATA_PATH = (
    ROOT / "frontend" / "src" / "data" / "feature_metadata.json"
)

EXPECTED_COUNT = 67
EXPECTED_GROUPS = ["CC", "dV", "CV", "dI", "Charge"]

REQUIRED_FIELDS = {
    "feature_id",
    "name",
    "order",
    "group",
    "description",
    "formula",
    "unit",
}


def main():
    print("\nVoltTwin Feature Metadata Validation")
    print("=" * 45)

    # Check file
    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            f"Metadata file not found: {METADATA_PATH}"
        )

    # Load JSON
    with METADATA_PATH.open(encoding="utf-8") as file:
        features = json.load(file)

    errors = []

    # 1. Feature count
    if len(features) != EXPECTED_COUNT:
        errors.append(
            f"Expected 67 features, found {len(features)}"
        )
    else:
        print(f"PASS: Feature count = {len(features)}")

    # 2. Required fields
    for index, feature in enumerate(features, start=1):
        missing = REQUIRED_FIELDS - feature.keys()

        if missing:
            errors.append(
                f"Feature {index}: missing fields {missing}"
            )

    if not errors:
        print("PASS: All required fields exist")

    # 3. Unique names
    names = [feature["name"] for feature in features]

    if len(names) != len(set(names)):
        errors.append("Duplicate feature names detected")
    else:
        print("PASS: Feature names are unique")

    # 4. Unique feature IDs
    ids = [feature["feature_id"] for feature in features]

    if len(ids) != len(set(ids)):
        errors.append("Duplicate feature IDs detected")
    else:
        print("PASS: Feature IDs are unique")

    # 5. Sequential ordering
    orders = [feature["order"] for feature in features]

    expected_orders = list(range(1, EXPECTED_COUNT + 1))

    if orders != expected_orders:
        errors.append(
            "Feature order is not sequential from 1 to 67"
        )
    else:
        print("PASS: Feature order is sequential")

    # 6. Group validation
    groups = list(
        dict.fromkeys(feature["group"] for feature in features)
    )

    if groups != EXPECTED_GROUPS:
        errors.append(
            f"Unexpected groups: {groups}"
        )
    else:
        print(f"PASS: Groups = {groups}")

    # 7. Group distribution
    counts = Counter(feature["group"] for feature in features)

    print("\nGroup distribution:")

    for group in EXPECTED_GROUPS:
        print(f"  {group}: {counts[group]}")

    # 8. Count unknown metadata values
    unknown_fields = ["description", "formula", "unit"]

    unknown_count = sum(
        1
        for feature in features
        for field in unknown_fields
        if feature.get(field) is None
    )

    print(f"\nUnknown metadata values (null): {unknown_count}")

    # Final report
    print("\n" + "=" * 45)

    if errors:
        print(f"FAIL: {len(errors)} issue(s) found")

        for error in errors:
            print(" -", error)

        raise SystemExit(1)

    print("PASS: Metadata structural validation successful")


if __name__ == "__main__":
    main()
