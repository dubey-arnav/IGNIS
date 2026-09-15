import { AlertTriangle } from "lucide-react";

export default function ErrorState({ message = "Unable to fetch data.", onRetry }) {
  return (
    <div className="state-block error">
      <AlertTriangle size={32} style={{ marginBottom: 12 }} />
      <span style={{ fontWeight: 600, fontSize: 15, marginBottom: 4 }}>Error Encountered</span>
      <span>{message}</span>
      {onRetry && (
        <button
          onClick={onRetry}
          style={{
            marginTop: 16,
            padding: "6px 14px",
            borderRadius: 6,
            border: "1px solid #B23A3A",
            background: "#FFFFFF",
            color: "#B23A3A",
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          Retry Request
        </button>
      )}
    </div>
  );
}
