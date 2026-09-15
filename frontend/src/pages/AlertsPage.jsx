import { useState } from "react";
import { Link } from "react-router-dom";
import { useFetch } from "../hooks/useFetch";
import { getAlerts } from "../api/alerts";
import PageContainer from "../components/layout/PageContainer";
import LoadingState from "../components/common/LoadingState";
import ErrorState from "../components/common/ErrorState";
import EmptyState from "../components/common/EmptyState";
import ClassificationBadge from "../components/event/ClassificationBadge";
import RiskBadge from "../components/event/RiskBadge";
import { ShieldAlert, MapPin, ArrowRight } from "lucide-react";

export default function AlertsPage() {
  const [selectedTier, setSelectedTier] = useState(null);
  const { data, loading, error, refetch } = useFetch(() => getAlerts(50), []);

  let filteredAlerts = data?.alerts || [];
  if (selectedTier) {
    filteredAlerts = filteredAlerts.filter((a) => a.risk.tier === selectedTier);
  }

  return (
    <PageContainer
      title="Industrial Thermal Anomaly Alerts"
      subtitle="High-priority Industrial Fire and Persistent Industrial Thermal Source detections"
    >
      {/* Tier Filters */}
      <div style={{ display: "flex", gap: 8, marginBottom: 20, flexWrap: "wrap", alignItems: "center" }}>
        <span style={{ fontSize: 12, fontWeight: 700, color: "var(--color-text-muted)", uppercase: true }}>
          Filter by Risk:
        </span>
        {["All", "Critical", "High", "Medium", "Low"].map((tier) => {
          const isActive = (tier === "All" && !selectedTier) || selectedTier === tier;
          return (
            <button
              key={tier}
              type="button"
              className={`filter-chip ${isActive ? "active" : ""}`}
              onClick={() => setSelectedTier(tier === "All" ? null : tier)}
            >
              {tier}
            </button>
          );
        })}
      </div>

      {loading ? (
        <LoadingState label="Scanning high-priority industrial alerts..." />
      ) : error ? (
        <ErrorState message="Could not fetch industrial alerts." onRetry={refetch} />
      ) : filteredAlerts.length === 0 ? (
        <EmptyState message="No high-priority industrial alerts matching selected filter." />
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          {filteredAlerts.map((alert) => (
            <div key={alert.event_id} className="card" style={{ padding: 18 }}>
              <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "center", gap: 16 }}>
                <div style={{ flex: 1, minWidth: 280 }}>
                  <div style={{ fontSize: 11, fontWeight: 600, color: "var(--color-text-muted)", marginBottom: 6 }}>
                    ALERT ID: {alert.event_id} · DETECTED {alert.event_date} {alert.event_time || ""}
                  </div>
                  <ClassificationBadge
                    label={alert.classification.label}
                    confidence={alert.classification.confidence}
                  />
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                  <RiskBadge
                    score={alert.risk.score}
                    tier={alert.risk.tier}
                    tierColor={alert.risk.tier_color}
                  />

                  <Link
                    to={`/map?event=${alert.event_id}`}
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: 6,
                      padding: "8px 16px",
                      backgroundColor: "var(--color-primary)",
                      color: "#FFFFFF",
                      borderRadius: "var(--radius-input)",
                      fontWeight: 600,
                      fontSize: 13,
                    }}
                  >
                    <MapPin size={14} />
                    Inspect on Map
                  </Link>
                </div>
              </div>

              {alert.nearby_facilities && alert.nearby_facilities.length > 0 && (
                <div style={{ marginTop: 12, paddingTop: 12, borderTop: "1px solid var(--color-border)", fontSize: 12, color: "var(--color-text-secondary)" }}>
                  <strong>Facility Proximity:</strong> {alert.nearby_facilities[0].name} ({Math.round(alert.nearby_facilities[0].distance_m)}m)
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </PageContainer>
  );
}
