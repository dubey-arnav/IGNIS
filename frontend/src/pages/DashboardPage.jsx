import { useFetch } from "../hooks/useFetch";
import { getDashboardSummary } from "../api/classifications";
import { getAlerts } from "../api/alerts";
import PageContainer from "../components/layout/PageContainer";
import LoadingState from "../components/common/LoadingState";
import ErrorState from "../components/common/ErrorState";
import ClassificationBadge from "../components/event/ClassificationBadge";
import RiskBadge from "../components/event/RiskBadge";
import { Link } from "react-router-dom";
import { ArrowRight, MapPin } from "lucide-react";

export default function DashboardPage() {
  const summary = useFetch(getDashboardSummary, []);
  const alerts = useFetch(() => getAlerts(4), []);

  if (summary.loading) {
    return (
      <PageContainer title="IGNIS Monitoring Dashboard">
        <LoadingState label="Loading thermal anomaly dashboard..." />
      </PageContainer>
    );
  }

  if (summary.error) {
    return (
      <PageContainer title="IGNIS Monitoring Dashboard">
        <ErrorState message="Could not connect to dashboard summary service." onRetry={summary.refetch} />
      </PageContainer>
    );
  }

  const { coverage, classification, risk } = summary.data;

  return (
    <PageContainer
      title="Industrial Thermal Monitoring"
      subtitle="AI-driven thermal anomaly classification & industrial fire monitoring system"
      headerAction={
        <Link
          to="/map"
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            padding: "10px 18px",
            backgroundColor: "var(--color-primary)",
            color: "#FFFFFF",
            borderRadius: "var(--radius-input)",
            fontWeight: 600,
            fontSize: 13,
            boxShadow: "var(--shadow-sm)",
          }}
        >
          <MapPin size={16} />
          Open Interactive Map
        </Link>
      }
    >
      {/* KPI Stat Cards */}
      <div className="stat-row">
        <div className="stat-card">
          <span className="stat-value">{coverage.total_events?.toLocaleString()}</span>
          <span className="stat-label">Total Thermal Detections</span>
        </div>

        <div className="stat-card">
          <span className="stat-value">{coverage.total_clusters?.toLocaleString()}</span>
          <span className="stat-label">Persistent Thermal Clusters</span>
        </div>

        <div className="stat-card">
          <span className="stat-value">{coverage.total_facilities?.toLocaleString()}</span>
          <span className="stat-label">Monitored Industrial Facilities</span>
        </div>

        <div className="stat-card">
          <span className="stat-value" style={{ color: "#C92A2A" }}>
            {(risk.tiers.find((t) => t.tier === "Critical")?.count || 0) +
              (risk.tiers.find((t) => t.tier === "High")?.count || 0)}
          </span>
          <span className="stat-label">High / Critical Risk Anomalies</span>
        </div>
      </div>

      {/* CLASSIFICATION BREAKDOWN — PRIMARY VISUAL BLOCK */}
      <section style={{ marginBottom: 32 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 12 }}>
          <h2 style={{ fontSize: 18, fontWeight: 700, color: "var(--color-heading)" }}>
            Classification Breakdown <span style={{ fontSize: 12, fontWeight: 500, color: "var(--color-text-muted)" }}>(Primary System Output)</span>
          </h2>
          <Link to="/analytics" style={{ fontSize: 13, fontWeight: 600 }}>View Full Analytics →</Link>
        </div>

        <div className="classification-grid">
          {classification.breakdown.map((item) => (
            <div key={item.label} className="classification-tile" style={{ borderColor: item.color }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span className="tile-label">{item.label}</span>
                <span
                  style={{
                    width: 10,
                    height: 10,
                    borderRadius: "50%",
                    backgroundColor: item.color,
                    display: "inline-block",
                  }}
                />
              </div>
              <span className="tile-count">{item.count.toLocaleString()}</span>
              <span className="tile-pct">{item.percentage}% of overall detections</span>
              {!item.modelled && <span className="tile-note">unmodelled baseline category</span>}
            </div>
          ))}
        </div>
      </section>

      {/* RISK TIERS — SECONDARY VISUAL BLOCK */}
      <section style={{ marginBottom: 32 }}>
        <h3 style={{ fontSize: 15, fontWeight: 700, color: "var(--color-text-secondary)", marginBottom: 12 }}>
          Risk Tiers <span style={{ fontSize: 12, fontWeight: 400 }}>(Secondary Evaluation Engine)</span>
        </h3>
        <div className="tier-row">
          {risk.tiers.map((t) => (
            <div key={t.tier} className="tier-chip" style={{ color: t.color, borderColor: "var(--color-border-card)" }}>
              <span>{t.tier}:</span> <strong>{t.count.toLocaleString()} events</strong>
            </div>
          ))}
        </div>
      </section>

      {/* RECENT ALERTS PREVIEW */}
      <section style={{ marginBottom: 32 }}>
        <div className="card">
          <div className="card-title">
            <span>Recent High-Priority Anomaly Alerts</span>
            <Link to="/alerts" style={{ fontSize: 13, fontWeight: 600 }}>View All Alerts →</Link>
          </div>

          {alerts.loading ? (
            <LoadingState label="Fetching recent alerts..." />
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {alerts.data?.alerts?.map((alert) => (
                <div key={alert.event_id} className="alert-row">
                  <div style={{ flex: 1 }}>
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
                    <span style={{ fontSize: 12, color: "var(--color-text-muted)", fontWeight: 500 }}>
                      {alert.event_date}
                    </span>
                    <Link
                      to={`/map?event=${alert.event_id}`}
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
                      Locate <ArrowRight size={12} />
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
    </PageContainer>
  );
}
