import client from "./client";
import { mockEvents } from "../data/mockData";

export async function getAlerts(limit = 25) {
  try {
    const res = await client.get("/api/alerts", { params: { limit } });
    return res.data;
  } catch (err) {
    console.warn("Backend offline. Using mock alerts data.", err.message);
    const industrialAlerts = mockEvents.filter(
      (ev) =>
        ev.classification.label === "Industrial Fire" ||
        ev.classification.label === "Persistent Industrial Thermal Source"
    );
    return {
      total: industrialAlerts.length,
      alerts: industrialAlerts.slice(0, limit),
    };
  }
}
