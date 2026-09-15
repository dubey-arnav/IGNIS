import client from "./client";
import { mockTimeline, mockDistanceProfile } from "../data/mockData";

export async function getTimeline(params = {}) {
  try {
    const res = await client.get("/api/analytics/timeline", { params });
    return res.data;
  } catch (err) {
    console.warn("Backend offline. Using mock analytics timeline.", err.message);
    return mockTimeline;
  }
}

export async function getByFacilityType() {
  try {
    const res = await client.get("/api/analytics/by-facility-type");
    return res.data;
  } catch (err) {
    console.warn("Backend offline. Using mock facility type breakdown.", err.message);
    return {
      items: [
        { facility_type: "Thermal Power Plant", count: 420 },
        { facility_type: "Petrochemical & Refinery", count: 380 },
        { facility_type: "Steel & Metallurgy", count: 340 },
        { facility_type: "Metallurgy & Smelting", count: 210 },
      ],
    };
  }
}

export async function getDistanceProfile() {
  try {
    const res = await client.get("/api/analytics/distance-profile");
    return res.data;
  } catch (err) {
    console.warn("Backend offline. Using mock distance profile data.", err.message);
    return mockDistanceProfile;
  }
}
