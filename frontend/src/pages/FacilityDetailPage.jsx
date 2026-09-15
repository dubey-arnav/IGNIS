import { useParams, Link } from "react-router-dom";
import { useFetch } from "../hooks/useFetch";
import { getFacility } from "../api/facilities";
import PageContainer from "../components/layout/PageContainer";
import LoadingState from "../components/common/LoadingState";
import ErrorState from "../components/common/ErrorState";
import ClassificationBadge from "../components/event/ClassificationBadge";
import RiskBadge from "../components/event/RiskBadge";
import { ArrowLeft, Building2, MapPin, Flame, ArrowRight } from "lucide-react";

export default function FacilityDetailPage() {
  const { id } = useParams();
  const { data, loading, error, refetch } = useFetch(() => getFacility(id), [id]);

  if (loading) {
    return (
      <PageContainer title="Facility Detail">
        <LoadingState label="Loading facility profile..." />
      </PageContainer>
    );
  }

  if (error || !data) {
    return (
      <PageContainer title="Facility Detail">
        <ErrorState message="Facility profile could not be retrieved." onRetry={refetch} />
      </PageContainer>
    );
  }

  return (
    <PageContainer
      title={data.name}
      subtitle={`${data.type} · ${data.nearby_event_count} nearby thermal detections`}
      headerAction={
        <Link
          to="/facilities"
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 6,
            padding: "8px 14px",
            backgroundColor: "var(--color-surface-alt)",
            color: "var(--color-text-secondary)",
            borderRadius: "var(--radius-input)",
            border: "1px solid var(--color-border)",
            fontWeight: 600,
            fontSize: 13,
          }}
        >
          <ArrowLeft size={14} /> Back to Directory
        </Link>
      }
    >
      <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
        {/* Facility Details Card */}
        <div className="card">
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16 }}>
            <div>
              <div style={{ fontSize: 12, color: "var(--color-text-muted)", fontWeight: 500 }}>Industrial Type</div>
              <div style={{ fontSize: 16, fontWeight: 700, color: "var(--color-heading)", marginTop: 2 }}>{data.type}</div>
            </div>

            <div>
              <div style={{ fontSize: 12, color: "var(--color-text-muted)", fontWeight: 500 }}>Location Coordinates</div>
              <div style={{ fontSize: 15, fontWeight: 600, color: "var(--color-primary)", marginTop: 2, display: "flex", alignItems: "center", gap: 4 }}>
                <MapPin size={14} />
                {data.latitude?.toFixed(4)}, {data.longitude?.toFixed(4)}
              </div>
            </div>

            <div>
              <div style={{ fontSize: 12, color: "var(--color-text-muted)", fontWeight: 500 }}>Thermal Anomaly Density</div>
              <div style={{ fontSize: 16, fontWeight: 700, color: "var(--color-heading)", marginTop: 2 }}>
                {data.nearby_event_count} detections within 2km
              </div>
            </div>
          </div>
        </div>

        {/* Classification Breakdown Nearby */}
        {data.classification_breakdown && (
          <div className="card">
            <h3 style={{ fontSize: 15, fontWeight: 700, color: "var(--color-heading)", marginBottom: 16 }}>
              Classification Distribution Nearby
            </h3>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
              {Object.entries(data.classification_breakdown).map(([label, count]) => (
                <div
                  key={label}
                  style={{
                    padding: "10px 16px",
                    backgroundColor: "var(--color-surface-alt)",
                    borderRadius: "var(--radius-card)",
                    border: "1px solid var(--color-border)",
                    display: "flex",
                    alignItems: "center",
                    gap: 10,
                  }}
                >
                  <span style={{ fontWeight: 600, fontSize: 13, color: "var(--color-text-primary)" }}>{label}</span>
                  <span style={{ fontWeight: 800, fontSize: 14, color: "var(--color-primary)", backgroundColor: "#FFFFFF", padding: "2px 8px", borderRadius: 12, border: "1px solid var(--color-border)" }}>
                    {count}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recent Events Nearby */}
        <div className="card">
          <div className="card-title">
            <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <Flame size={18} color="var(--color-primary)" />
              Recent Thermal Detections Near Facility
            </span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 12, marginTop: 12 }}>
            {data.recent_events?.map((event) => (
              <div key={event.event_id} className="alert-row">
                <div style={{ flex: 1 }}>
                  <ClassificationBadge
                    label={event.classification.label}
                    confidence={event.classification.confidence}
                  />
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                  <RiskBadge
                    score={event.risk.score}
                    tier={event.risk.tier}
                    tierColor={event.risk.tier_color}
                  />
                  <span style={{ fontSize: 12, color: "var(--color-text-muted)" }}>
                    {event.event_date}
                  </span>
                  <Link
                    to={`/map?event=${event.event_id}`}
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: 4,
                      fontSize: 12,
                      fontWeight: 600,
                      padding: "6px 12px",
                      backgroundColor: "var(--color-surface-alt)",
                      borderRadius: "var(--radius-input)",
                      border: "1px solid var(--color-border)",
                    }}
                  >
                    View on Map <ArrowRight size={12} />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
