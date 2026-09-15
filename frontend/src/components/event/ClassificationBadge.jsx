import { classificationMeta } from "../../constants/classification";

export default function ClassificationBadge({ label, confidence }) {
  const meta = classificationMeta(label);

  return (
    <div className="classification-badge" style={{ borderColor: meta.color }}>
      <span
        style={{
          width: 12,
          height: 12,
          borderRadius: "50%",
          backgroundColor: meta.color,
          display: "inline-block",
          flexShrink: 0,
        }}
      />
      <div>
        <div className="classification-label" style={{ color: meta.color }}>
          {label}
        </div>
        {confidence != null && (
          <div className="classification-confidence">
            {Math.round(confidence * (confidence <= 1 ? 100 : 1))}% Confidence
          </div>
        )}
      </div>
    </div>
  );
}
