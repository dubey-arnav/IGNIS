import { Inbox } from "lucide-react";

export default function EmptyState({ message = "No records match your criteria." }) {
  return (
    <div className="state-block empty">
      <Inbox size={32} style={{ marginBottom: 12, opacity: 0.5 }} />
      <span>{message}</span>
    </div>
  );
}
