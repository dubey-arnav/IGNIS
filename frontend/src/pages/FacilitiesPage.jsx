import { useState } from "react";
import { Link } from "react-router-dom";
import { useFetch } from "../hooks/useFetch";
import { listFacilities } from "../api/facilities";
import PageContainer from "../components/layout/PageContainer";
import LoadingState from "../components/common/LoadingState";
import ErrorState from "../components/common/ErrorState";
import EmptyState from "../components/common/EmptyState";
import { Search, Building2, ArrowRight } from "lucide-react";

export default function FacilitiesPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const { data, loading, error, refetch } = useFetch(
    () => listFacilities({ q: searchTerm || undefined, limit: 100 }),
    [searchTerm]
  );

  return (
    <PageContainer
      title="Monitored Industrial Facilities"
      subtitle="Searchable registry of industrial plants, power stations, refineries, and metallurgy hubs"
    >
      <div style={{ position: "relative", maxWidth: 450 }}>
        <Search
          size={18}
          color="var(--color-text-muted)"
          style={{ position: "absolute", left: 14, top: 12 }}
        />
        <input
          type="text"
          className="search-input"
          style={{ paddingLeft: 42 }}
          placeholder="Search by facility name or industrial type..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {loading ? (
        <LoadingState label="Loading facility directory..." />
      ) : error ? (
        <ErrorState message="Failed to load facilities directory." onRetry={refetch} />
      ) : data?.items?.length === 0 ? (
        <EmptyState message="No facilities matched your search query." />
      ) : (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Facility Name</th>
                <th>Industrial Type</th>
                <th>Coordinates</th>
                <th>Nearby Anomalies</th>
                <th style={{ textAlign: "right" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((facility) => (
                <tr key={facility.id}>
                  <td>
                    <div style={{ fontWeight: 600, color: "var(--color-heading)", display: "flex", alignItems: "center", gap: 8 }}>
                      <Building2 size={16} color="var(--color-primary)" />
                      {facility.name}
                    </div>
                  </td>
                  <td>
                    <span
                      style={{
                        fontSize: 12,
                        padding: "3px 8px",
                        backgroundColor: "var(--color-surface-alt)",
                        borderRadius: "var(--radius-input)",
                        border: "1px solid var(--color-border)",
                        fontWeight: 500,
                      }}
                    >
                      {facility.type}
                    </span>
                  </td>
                  <td style={{ color: "var(--color-text-muted)" }}>
                    {facility.latitude?.toFixed(4)}, {facility.longitude?.toFixed(4)}
                  </td>
                  <td>
                    <span style={{ fontWeight: 700, color: "var(--color-primary)" }}>
                      {facility.nearby_event_count} detections
                    </span>
                  </td>
                  <td style={{ textAlign: "right" }}>
                    <Link
                      to={`/facilities/${facility.id}`}
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        gap: 4,
                        fontSize: 12,
                        fontWeight: 600,
                        padding: "6px 12px",
                        backgroundColor: "var(--color-onboard-bg)",
                        color: "var(--color-primary)",
                        borderRadius: "var(--radius-input)",
                      }}
                    >
                      Inspect <ArrowRight size={12} />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </PageContainer>
  );
}
