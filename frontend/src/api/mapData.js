import client from "./client";
import { mockMapData } from "../data/mockData";

export async function getMapData(params = {}) {
  try {
    const res = await client.get("/api/map-data", { params });
    return res.data;
  } catch (err) {
    console.warn("Backend offline or request failed. Using mock map data.", err.message);
    let features = [...mockMapData.features];
    if (params.classification) {
      const cls = Array.isArray(params.classification) ? params.classification : [params.classification];
      features = features.filter((f) => cls.includes(f.properties.classification));
    }
    if (params.tier) {
      const tiers = Array.isArray(params.tier) ? params.tier : [params.tier];
      features = features.filter((f) => tiers.includes(f.properties.risk_tier));
    }
    return {
      type: "FeatureCollection",
      features,
    };
  }
}
