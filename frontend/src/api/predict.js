import client from "./client";
import { mockDashboardSummary } from "../data/mockData";

export async function predictEvent(payload) {
  try {
    const res = await client.post("/api/predict", payload);
    return res.data;
  } catch (err) {
    console.warn("Backend offline. Returning mock prediction.", err.message);
    return {
      prediction: "Industrial Fire",
      confidence: 0.94,
      class_probabilities: {
        "Industrial Fire": 0.94,
        "Persistent Industrial Thermal Source": 0.04,
        "Wildfire / Natural Fire": 0.01,
        "Other/Unknown": 0.01,
      },
      risk: { score: 87, tier: "Critical", tier_color: "#C92A2A" },
    };
  }
}

export async function getModelInfo() {
  try {
    const res = await client.get("/api/model-info");
    return res.data;
  } catch (err) {
    console.warn("Backend offline. Using mock model info.", err.message);
    return mockDashboardSummary.model;
  }
}
