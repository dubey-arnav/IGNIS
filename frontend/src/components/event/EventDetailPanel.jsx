import { useFetch } from "../../hooks/useFetch";
import { getEvent } from "../../api/events";
import ClassificationBadge from "./ClassificationBadge";
import RiskBadge from "./RiskBadge";
import LoadingState from "../common/LoadingState";
import ErrorState from "../common/ErrorState";
import { X, Flame, Clock, Building2, ShieldAlert } from "lucide-react";

export default function EventDetailPanel({ eventId, onClose }) {
  const { data, loading, error, refetch } = useFetch(() => getEvent(eventId), [eventId]);

  return (
    <aside className="event-detail-panel">
      <button className="panel-close" onClick={onClose} aria-label="Close event panel">
        <X size={16} />
      </button>

      {loading && <LoadingState label="Fetching event details..." />}
      {error && <ErrorState message="Could not load event detail." onRetry={refetch} />}

      {data && (
        <>
          <div style={{ marginTop: 12 }}>
            <div style={{ fontSize: 11, fontWeight: 600, color: "var(--color-text-muted)", textTransform: "uppercase", marginBottom: 6 }}>
              Event ID: {data.event_id}
            </div>
            {/* CLASSIFICATION FIRST */}
            <ClassificationBadge
              label={data.classification.label}
              confidence={data.classification.confidence}
            />
          </div>

          {/* RISK SECOND */}
          <div>
            <RiskBadge
              score={data.risk.score}
              tier={data.risk.tier}
              tierColor={data.risk.tier_color}
            />
          </div>

          <section className="panel-section">
            <h4 style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <Flame size={14} color="var(--color-primary)" />
              Thermal Detection
            </h4>
            <dl className="data-dl">
              <dt>Detection Date</dt>
              <dd>{data.event_date} {data.event_time || ""}</dd>
              <dt>Fire Radiative Power</dt>
              <dd>{data.frp ?? "—"} MW</dd>
              <dt>Brightness</dt>
              <dd>{data.brightness ? `${data.brightness} K` : "—"}</dd>
              <dt>Satellite / Sensor</dt>
              <dd>{data.satellite || "—"} / {data.instrument || "—"}</dd>
              <dt>FIRMS Confidence</dt>
              <dd>{data.sensor_confidence || "—"}</dd>
              <dt>Day / Night</dt>
              <dd>{data.daynight === "D" ? "Daytime" : data.daynight === "N" ? "Nighttime" : "—"}</dd>
              <dt>Coordinates</dt>
              <dd>{data.latitude?.toFixed(4)}, {data.longitude?.toFixed(4)}</dd>
            </dl>
          </section>

          {data.cluster && (
            <section className="panel-section">
              <h4 style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <Clock size={14} color="var(--color-primary)" />
                Historical Persistence
              </h4>
              <dl className="data-dl">
                <dt>First Detected</dt>
                <dd>{data.cluster.first_detection || "—"}</dd>
                <dt>Last Detected</dt>
                <dd>{data.cluster.last_detection || "—"}</dd>
                <dt>Total Detections</dt>
                <dd>{data.cluster.total_detections ?? "—"}</dd>
                <dt>Active Days</dt>
                <dd>{data.cluster.active_days ?? "—"}</dd>
                <dt>Persistence Score</dt>
                <dd>{data.cluster.persistence_score ? `${(data.cluster.persistence_score * 100).toFixed(0)}%` : "—"}</dd>
              </dl>
            </section>
          )}

          {data.nearby_facilities && data.nearby_facilities.length > 0 && (
            <section className="panel-section">
              <h4 style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <Building2 size={14} color="var(--color-primary)" />
                Nearby Facilities
              </h4>
              <ul style={{ listStyle: "none", padding: 0, display: "flex", flexDirection: "column", gap: 8 }}>
                {data.nearby_facilities.map((fac) => (
                  <li
                    key={fac.id}
                    style={{
                      padding: 10,
                      backgroundColor: "var(--color-surface-alt)",
                      borderRadius: "var(--radius-input)",
                      border: "1px solid var(--color-border)",
                      fontSize: 13,
                    }}
                  >
                    <div style={{ fontWeight: 600, color: "var(--color-heading)" }}>{fac.name}</div>
                    <div style={{ display: "flex", justifyContent: "space-between", marginTop: 4, color: "var(--color-text-muted)", fontSize: 12 }}>
                      <span>{fac.type}</span>
                      <span style={{ fontWeight: 600, color: "var(--color-primary)" }}>{Math.round(fac.distance_m)} m away</span>
                    </div>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </>
      )}
    </aside>
  );
}
