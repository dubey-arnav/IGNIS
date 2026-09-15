import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { CLASSIFICATIONS } from "../../constants/classification";

const BUCKET_ORDER = ["0-500m", "500-1500m", "1.5-5km", "5-10km", ">10km"];

export default function DistanceProfileChart({ items = [] }) {
  const byBucket = {};
  items.forEach((row) => {
    if (!byBucket[row.bucket]) {
      byBucket[row.bucket] = { bucket: row.bucket };
    }
    byBucket[row.bucket][row.predicted_label] = row.count;
  });

  const chartData = BUCKET_ORDER.map((bucket) => byBucket[bucket] || { bucket });
  const modelledLabels = Object.keys(CLASSIFICATIONS).filter(
    (label) => CLASSIFICATIONS[label].modelled
  );

  return (
    <div style={{ width: "100%", height: 320 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E6ECF3" />
          <XAxis dataKey="bucket" tick={{ fontSize: 12, fill: "#44566B" }} />
          <YAxis tick={{ fontSize: 11, fill: "#44566B" }} />
          <Tooltip
            contentStyle={{
              backgroundColor: "#FFFFFF",
              borderColor: "#D8E2EE",
              borderRadius: 8,
              fontSize: 12,
            }}
          />
          <Legend wrapperStyle={{ fontSize: 12, paddingTop: 10 }} />
          {modelledLabels.map((label) => (
            <Bar
              key={label}
              dataKey={label}
              stackId="a"
              fill={CLASSIFICATIONS[label].color}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
