import { useEffect, useState, useCallback } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import icon from "leaflet/dist/images/marker-icon.png";
import iconShadow from "leaflet/dist/images/marker-shadow.png";
import { getMapData } from "../../api/mapData";
import { classificationMeta, riskTierMeta } from "../../constants/classification";
import MapLegend from "./MapLegend";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: icon,
  shadowUrl: iconShadow,
});

const DEFAULT_CENTER = [22.5, 79.0];
const DEFAULT_ZOOM = 5;

function BoundsWatcher({ onBoundsChange }) {
  const map = useMap();

  const handleMoveEnd = useCallback(() => {
    const bounds = map.getBounds();
    onBoundsChange([
      bounds.getWest(),
      bounds.getSouth(),
      bounds.getEast(),
      bounds.getNorth(),
    ]);
  }, [map, onBoundsChange]);

  useEffect(() => {
    map.on("moveend", handleMoveEnd);
    handleMoveEnd();
    return () => {
      map.off("moveend", handleMoveEnd);
    };
  }, [map, handleMoveEnd]);

  return null;
}

export default function FireMap({ filters = {}, onSelectEvent }) {
  const [features, setFeatures] = useState([]);
  const [bbox, setBbox] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    const params = { ...filters, limit: 5000 };
    if (bbox) {
      params.bbox = bbox.join(",");
    }

    getMapData(params)
      .then((geojson) => {
        if (!cancelled && geojson?.features) {
          setFeatures(geojson.features);
        }
      })
      .catch((err) => {
        console.error("Map fetch error:", err);
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [filters, bbox]);

  return (
    <div className="map-wrapper">
      {loading && (
        <div style={{ position: "absolute", top: 12, right: 12, zIndex: 1000, background: "rgba(255,255,255,0.9)", padding: "4px 12px", borderRadius: 20, boxShadow: "var(--shadow-sm)", fontSize: 12, fontWeight: 600 }}>
          Updating Map Data...
        </div>
      )}
      <MapContainer
        center={DEFAULT_CENTER}
        zoom={DEFAULT_ZOOM}
        style={{ height: "100%", width: "100%" }}
        zoomControl={true}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        <BoundsWatcher onBoundsChange={setBbox} />

        {features.map((feature) => {
          const coords = feature.geometry?.coordinates;
          if (!coords || coords.length < 2) return null;
          const [lon, lat] = coords;
          const props = feature.properties || {};
          const meta = classificationMeta(props.classification);
          const riskMeta = riskTierMeta(props.risk_tier);

          return (
            <CircleMarker
              key={props.event_id}
              center={[lat, lon]}
              radius={7}
              pathOptions={{
                color: meta.color,
                fillColor: meta.color,
                fillOpacity: 0.85,
                weight: 2,
              }}
              eventHandlers={{
                click: () => onSelectEvent(props.event_id),
              }}
            >
              <Popup>
                <div style={{ padding: 4, fontFamily: "Inter, sans-serif" }}>
                  <div style={{ fontWeight: 700, color: meta.color, fontSize: 14, marginBottom: 4, display: "flex", alignItems: "center" }}>
                    <span style={{ width: 8, height: 8, borderRadius: "50%", backgroundColor: meta.color, display: "inline-block", marginRight: 6 }} />
                    {props.classification}
                  </div>
                  <div style={{ fontSize: 12, color: "#44566B" }}>
                    <div><strong>Date:</strong> {props.event_date}</div>
                    <div><strong>FRP:</strong> {props.frp ?? "—"} MW</div>
                    <div>
                      <strong>Risk Tier:</strong>{" "}
                      <span style={{ color: riskMeta.color, fontWeight: 700 }}>
                        {props.risk_tier || "Low"}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => onSelectEvent(props.event_id)}
                    style={{
                      marginTop: 8,
                      width: "100%",
                      padding: "4px 8px",
                      borderRadius: 4,
                      border: "none",
                      backgroundColor: "var(--color-primary)",
                      color: "#FFFFFF",
                      fontSize: 12,
                      fontWeight: 600,
                      cursor: "pointer",
                    }}
                  >
                    Inspect Event →
                  </button>
                </div>
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>
      <MapLegend />
    </div>
  );
}
