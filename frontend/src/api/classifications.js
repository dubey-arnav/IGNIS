import client from "./client";
import { mockDashboardSummary } from "../data/mockData";

export async function getClassifications() {
  try {
    const res = await client.get("/api/classifications");
    return res.data;
  } catch (err) {
    console.warn("Backend offline. Using mock classifications.", err.message);
    return {
      classifications: mockDashboardSummary.classification.breakdown,
    };
  }
}

export async function getDashboardSummary() {
  try {
    const res = await client.get("/api/dashboard-summary");
    return res.data;
  } catch (err) {
    console.warn("Backend offline. Using mock dashboard summary.", err.message);
    return mockDashboardSummary;
  }
}
