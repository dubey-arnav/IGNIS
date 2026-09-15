import client from "./client";
import { mockFacilities, mockEvents } from "../data/mockData";

export async function listFacilities(params = {}) {
  try {
    const res = await client.get("/api/facilities", { params });
    return res.data;
  } catch (err) {
    console.warn("Backend offline. Using mock facility list.", err.message);
    let items = [...mockFacilities];
    if (params.q) {
      const q = params.q.toLowerCase();
      items = items.filter(
        (f) => f.name.toLowerCase().includes(q) || f.type.toLowerCase().includes(q)
      );
    }
    return {
      total: items.length,
      limit: params.limit || 50,
      offset: params.offset || 0,
      items,
    };
  }
}

export async function getFacilityTypes() {
  try {
    const res = await client.get("/api/facilities/types");
    return res.data;
  } catch (err) {
    console.warn("Backend offline. Using mock facility types.", err.message);
    return {
      types: [
        "Petrochemical & Refinery",
        "Thermal Power Plant",
        "Steel & Metallurgy",
        "Metallurgy & Smelting",
      ],
    };
  }
}

export async function getFacility(facilityId) {
  try {
    const res = await client.get(`/api/facilities/${facilityId}`);
    return res.data;
  } catch (err) {
    console.warn(`Backend offline. Using mock detail for facility ${facilityId}.`, err.message);
    const fac = mockFacilities.find((f) => f.id === facilityId) || mockFacilities[0];
    const recent = mockEvents.filter((ev) =>
      ev.nearby_facilities.some((nf) => nf.id === fac.id)
    );
    return {
      ...fac,
      recent_events: recent.length > 0 ? recent : mockEvents.slice(0, 3),
    };
  }
}
