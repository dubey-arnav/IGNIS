export const CLASSIFICATIONS = {
  "Industrial Fire": {
    code: "industrial_fire",
    color: "#E03131",
    modelled: true,
    priority: 1,
    description: "High-intensity thermal source directly adjacent to known industrial facility infrastructure.",
  },
  "Persistent Industrial Thermal Source": {
    code: "persistent_industrial",
    color: "#F76707",
    modelled: true,
    priority: 2,
    description: "Recurring operational thermal emissions (flaring, furnaces, kilns) with long historical persistence.",
  },
  "Wildfire / Natural Fire": {
    code: "wildfire",
    color: "#F59F00",
    modelled: true,
    priority: 3,
    description: "Vegetation or forest fire detected far from industrial structures.",
  },
  "Agricultural Burning": {
    code: "agricultural_burning",
    color: "#66A80F",
    modelled: false,
    priority: 4,
    description: "Seasonal crop residue burning detected in farmland regions (unmodelled baseline).",
  },
  "Other/Unknown": {
    code: "other_unknown",
    color: "#868E96",
    modelled: true,
    priority: 5,
    description: "Thermal anomaly without strong industrial or vegetation signature match.",
  },
};

export const RISK_TIERS = {
  Critical: { color: "#C92A2A", bg: "#FCE8E8", text: "#B23A3A", minScore: 70 },
  High: { color: "#E8590C", bg: "#FFF7ED", text: "#D97706", minScore: 40 },
  Medium: { color: "#F08C00", bg: "#FEF3C7", text: "#B45309", minScore: 15 },
  Low: { color: "#475569", bg: "#F1F5F9", text: "#475569", minScore: 0 },
};

export function classificationMeta(label) {
  return CLASSIFICATIONS[label] || CLASSIFICATIONS["Other/Unknown"];
}

export function riskTierMeta(tier) {
  return RISK_TIERS[tier] || RISK_TIERS["Low"];
}
