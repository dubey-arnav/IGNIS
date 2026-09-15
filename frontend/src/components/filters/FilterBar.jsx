import { CLASSIFICATIONS, RISK_TIERS } from "../../constants/classification";
import { Filter, X } from "lucide-react";

export default function FilterBar({ filters = {}, onChange }) {
  const selectedClassifications = filters.classification || [];
  const selectedTiers = filters.tier || [];

  const toggleClassification = (label) => {
    const next = selectedClassifications.includes(label)
      ? selectedClassifications.filter((c) => c !== label)
      : [...selectedClassifications, label];
    onChange({ ...filters, classification: next.length ? next : undefined });
  };

  const toggleTier = (tier) => {
    const next = selectedTiers.includes(tier)
      ? selectedTiers.filter((t) => t !== tier)
      : [...selectedTiers, tier];
    onChange({ ...filters, tier: next.length ? next : undefined });
  };

  const clearAll = () => {
    onChange({});
  };

  const hasActiveFilters = selectedClassifications.length > 0 || selectedTiers.length > 0;

  return (
    <div className="filter-bar">
      <div style={{ display: "flex", alignItems: "center", gap: 6, color: "var(--color-primary)", fontWeight: 700, fontSize: 13 }}>
        <Filter size={16} />
        <span>FILTERS:</span>
      </div>

      {/* Primary Group — Classification */}
      <div className="filter-group">
        <span className="filter-group-label">Classification (Primary)</span>
        {Object.entries(CLASSIFICATIONS).map(([label, meta]) => {
          const isActive = selectedClassifications.includes(label);
          return (
            <button
              key={label}
              type="button"
              className={`filter-chip ${isActive ? "active" : ""}`}
              onClick={() => toggleClassification(label)}
            >
              <span className="legend-dot" style={{ backgroundColor: meta.color, width: 8, height: 8 }} />
              <span>{label}</span>
            </button>
          );
        })}
      </div>

      {/* Secondary Group — Risk Tier */}
      <div className="filter-group filter-group-secondary">
        <span className="filter-group-label">Risk Tier (Secondary)</span>
        {Object.keys(RISK_TIERS).map((tier) => {
          const isActive = selectedTiers.includes(tier);
          const meta = RISK_TIERS[tier];
          return (
            <button
              key={tier}
              type="button"
              className={`filter-chip ${isActive ? "active" : ""}`}
              onClick={() => toggleTier(tier)}
              style={isActive ? { borderColor: meta.color, color: meta.color } : {}}
            >
              <span className="legend-dot" style={{ backgroundColor: meta.color, width: 8, height: 8 }} />
              <span>{tier}</span>
            </button>
          );
        })}
      </div>

      {hasActiveFilters && (
        <button
          type="button"
          onClick={clearAll}
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 4,
            padding: "4px 10px",
            fontSize: 12,
            borderRadius: "var(--radius-pill)",
            border: "1px solid var(--color-border)",
            background: "var(--color-surface-alt)",
            color: "var(--color-text-secondary)",
            cursor: "pointer",
            marginLeft: "auto",
          }}
        >
          <X size={12} />
          Clear Filters
        </button>
      )}
    </div>
  );
}
