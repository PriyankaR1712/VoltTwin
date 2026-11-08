
import "./FeatureExplorer.css";
import { useState } from "react";
import featureMetadata from "../data/feature_metadata.json";

type Feature = {
  feature_id: string;
  name: string;
  order: number;
  group: string;
  description: string | null;
  formula: string | null;
  unit: string | null;
};

const features = featureMetadata as Feature[];

const groups = ["All", "CC", "dV", "CV", "dI", "Charge"];

export default function FeatureExplorer() {
  const [search, setSearch] = useState("");
  const [selectedGroup, setSelectedGroup] = useState("All");
  const [selectedFeature, setSelectedFeature] =
    useState<Feature | null>(features[0] ?? null);
  const [compareFeatures, setCompareFeatures] = useState<Feature[]>([]);

  const filteredFeatures = features.filter((feature) => {
    const searchText = search.toLowerCase();

    const matchesSearch =
      feature.name.toLowerCase().includes(searchText) ||
      feature.feature_id.toLowerCase().includes(searchText);

    const matchesGroup =
      selectedGroup === "All" || feature.group === selectedGroup;

    return matchesSearch && matchesGroup;
  });

  const groupCount =
    selectedGroup === "All"
      ? features.length
      : features.filter((feature) => feature.group === selectedGroup).length;

  const toggleCompareFeature = (feature: Feature) => {
    setCompareFeatures((current) => {
      const exists = current.some(
        (item) => item.feature_id === feature.feature_id
      );

      if (exists) {
        return current.filter(
          (item) => item.feature_id !== feature.feature_id
        );
      }

      if (current.length >= 4) {
        return current;
      }

      return [...current, feature];
    });
  };

  const removeCompareFeature = (featureId: string) => {
    setCompareFeatures((current) =>
      current.filter((feature) => feature.feature_id !== featureId)
    );
  };

  const clearComparison = () => {
    setCompareFeatures([]);
  };

  const isCompared = (featureId: string) =>
    compareFeatures.some((item) => item.feature_id === featureId);

  const handleFeatureKeyDown = (
    event: React.KeyboardEvent<HTMLDivElement>,
    feature: Feature
  ) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      setSelectedFeature(feature);
    }
  };

  return (
    <div className="feature-explorer">
      {/* Header */}
      <header className="feature-header">
        <div>
          <h1>Feature Explorer</h1>
          <p>Explore and compare the 67 XJTU handcrafted battery features</p>
        </div>

        <span className="feature-count">
          {features.length} Features
        </span>
      </header>

      {/* Feature list and details */}
      <div className="feature-layout">
        {/* Feature List */}
        <section className="feature-list-panel">

          {/* Feature Statistics */}
          <div className="feature-stats-card">
            <div className="feature-stats-icon">
              <span>⌘</span>
            </div>

            <div className="feature-stats-content">
              <div className="feature-stats-top">
                <strong>{filteredFeatures.length}</strong>
                <span className="feature-stats-label">
                  {selectedGroup === "All" ? "Features" : selectedGroup}
                </span>
              </div>

              <p>
                {search
                  ? "Matching features"
                  : selectedGroup === "All"
                  ? "Handcrafted battery feature inputs"
                  : `${selectedGroup} feature group`}
              </p>

              <div className="feature-stats-footer">
                <span className="feature-stats-dot" />
                {selectedGroup === "All"
                  ? "5 feature groups"
                  : `${groupCount} features in group`}
              </div>
            </div>
          </div>

          <input
            type="text"
            placeholder="Search features..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            className="feature-search"
            aria-label="Search features"
          />

          <div className="feature-groups">
            {groups.map((group) => (
              <button
                key={group}
                className={selectedGroup === group ? "active" : ""}
                onClick={() => setSelectedGroup(group)}
              >
                {group}
              </button>
            ))}
          </div>

          <div className="feature-list">
            {filteredFeatures.map((feature) => (
              <div
                key={feature.feature_id}
                className={`feature-item ${
                  selectedFeature?.feature_id === feature.feature_id
                    ? "selected"
                    : ""
                }`}
                role="button"
                tabIndex={0}
                onClick={() => setSelectedFeature(feature)}
                onKeyDown={(event) =>
                  handleFeatureKeyDown(event, feature)
                }
              >
                <span>{feature.name}</span>

                <div className="feature-item-actions">
                  <small>#{feature.order}</small>

                  <input
                    type="checkbox"
                    checked={isCompared(feature.feature_id)}
                    onChange={() => toggleCompareFeature(feature)}
                    onClick={(event) => event.stopPropagation()}
                    onKeyDown={(event) => event.stopPropagation()}
                    title={
                      isCompared(feature.feature_id)
                        ? "Remove from comparison"
                        : "Add to comparison"
                    }
                    aria-label={`Compare ${feature.name}`}
                  />
                </div>
              </div>
            ))}

            {filteredFeatures.length === 0 && (
              <p className="no-features">No features found.</p>
            )}
          </div>

          {compareFeatures.length === 4 && (
            <p className="no-features">
              Maximum of 4 features selected.
            </p>
          )}
        </section>

        {/* Feature Details */}
        <section className="feature-details-panel">
          {selectedFeature ? (
            <>
              <span className="feature-badge">
                {selectedFeature.group}
              </span>

              <h2>{selectedFeature.name}</h2>

              <p className="feature-id">
                ID: {selectedFeature.feature_id}
              </p>

              <div className="feature-detail">
                <h3>Description</h3>
                <p>
                  {selectedFeature.description ??
                    "Description not verified yet."}
                </p>
              </div>

              <div className="feature-detail">
                <h3>Formula</h3>
                <p>
                  {selectedFeature.formula ??
                    "Formula not verified yet."}
                </p>
              </div>

              <div className="feature-detail">
                <h3>Unit</h3>
                <p>
                  {selectedFeature.unit ??
                    "Unit not verified yet."}
                </p>
              </div>

              <div className="feature-detail">
                <h3>Original Feature Order</h3>
                <p>{selectedFeature.order} / 67</p>
              </div>

              <button
                className="comparison-header button"
                onClick={() => toggleCompareFeature(selectedFeature)}
                disabled={
                  !isCompared(selectedFeature.feature_id) &&
                  compareFeatures.length >= 4
                }
              >
                {isCompared(selectedFeature.feature_id)
                  ? "Remove from Comparison"
                  : "Add to Comparison"}
              </button>
            </>
          ) : (
            <p>Select a feature to view its details.</p>
          )}
        </section>
      </div>

      {/* Feature Comparison */}
      <section className="feature-comparison-panel">
        <div className="comparison-header">
          <div>
            <h2>Feature Comparison</h2>
            <p>
              Compare metadata for up to 4 selected features.
            </p>
          </div>

          <button
            className="comparison-clear"
            onClick={clearComparison}
            disabled={compareFeatures.length === 0}
          >
            Clear All
          </button>
        </div>

        {compareFeatures.length === 0 ? (
          <div className="comparison-empty">
            <p>No features selected for comparison.</p>
            <p>
              Select the checkboxes beside features to compare them here.
            </p>
          </div>
        ) : (
          <div className="comparison-grid">
            {compareFeatures.map((feature) => (
              <article
                className="comparison-card"
                key={feature.feature_id}
              >
                <div className="comparison-card-header">
                  <span className="feature-badge">
                    {feature.group}
                  </span>

                  <button
                    className="comparison-remove"
                    onClick={() =>
                      removeCompareFeature(feature.feature_id)
                    }
                    aria-label={`Remove ${feature.name}`}
                    title="Remove feature"
                  >
                    ×
                  </button>
                </div>

                <h3 className="comparison-feature-name">
                  {feature.name}
                </h3>

                <p className="comparison-feature-id">
                  {feature.feature_id}
                </p>

                <div className="comparison-info">
                  <span>Original Order</span>
                  <strong>{feature.order} / 67</strong>
                </div>

                <div className="comparison-info">
                  <span>Description</span>
                  <strong>
                    {feature.description ?? "Not verified yet"}
                  </strong>
                </div>

                <div className="comparison-info">
                  <span>Formula</span>
                  <strong>
                    {feature.formula ?? "Not verified yet"}
                  </strong>
                </div>

                <div className="comparison-info">
                  <span>Unit</span>
                  <strong>
                    {feature.unit ?? "Not verified yet"}
                  </strong>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
