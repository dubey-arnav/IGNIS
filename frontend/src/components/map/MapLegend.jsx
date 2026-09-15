import { CLASSIFICATIONS } from "../../constants/classification";

export default function MapLegend() {
  const sortedClassifications = Object.entries(CLASSIFICATIONS).sort(
    (a, b) => a[1].priority - b[1].priority
  );

  return (
    <div className="map-legend">
      <div className="legend-title">Classification Legend</div>
      {sortedClassifications.map(([label, meta]) => (
        <div key={label} className="legend-row">
          <span className="legend-dot" style={{ backgroundColor: meta.color }} />
          <span>
            {label} {!meta.modelled && <em style={{ fontSize: 10, color: "var(--color-text-dim)" }}>(unmodelled)</em>}
          </span>
        </div>
      ))}
    </div>
  );
}
