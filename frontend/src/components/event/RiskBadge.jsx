import { riskTierMeta } from "../../constants/classification";

export default function RiskBadge({ score, tier, tierColor }) {
  const meta = riskTierMeta(tier);
  const color = tierColor || meta.color;

  return (
    <div className="risk-badge" style={{ borderColor: color, color: color }}>
      <span className="risk-label">Risk Score</span>
      <span className="risk-score">{score ?? "—"}</span>
      <span className="risk-tier" style={{ color: color }}>
        {tier || "Low"}
      </span>
    </div>
  );
}
