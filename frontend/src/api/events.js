import client from "./client";
import { mockEvents } from "../data/mockData";

export async function listEvents(params = {}) {
  try {
    const res = await client.get("/api/events", { params });
    return res.data;
  } catch (err) {
    console.warn("Backend offline or request failed. Using mock event list.", err.message);
    let filtered = [...mockEvents];
    if (params.classification && params.classification.length) {
      const cls = Array.isArray(params.classification) ? params.classification : [params.classification];
      filtered = filtered.filter((ev) => cls.includes(ev.classification.label));
    }
    if (params.tier && params.tier.length) {
      const tiers = Array.isArray(params.tier) ? params.tier : [params.tier];
      filtered = filtered.filter((ev) => tiers.includes(ev.risk.tier));
    }
    return {
      total: filtered.length,
      limit: params.limit || 50,
      offset: params.offset || 0,
      items: filtered,
    };
  }
}

export async function getEvent(eventId) {
  try {
    const res = await client.get(`/api/events/${eventId}`);
    return res.data;
  } catch (err) {
    console.warn(`Backend offline or request failed for event ${eventId}. Using mock event.`, err.message);
    const found = mockEvents.find((e) => e.event_id === eventId);
    return found || mockEvents[0];
  }
}
