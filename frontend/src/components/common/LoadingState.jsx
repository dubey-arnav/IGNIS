export default function LoadingState({ label = "Loading data..." }) {
  return (
    <div className="state-block loading">
      <div className="spinner" />
      <span>{label}</span>
    </div>
  );
}
