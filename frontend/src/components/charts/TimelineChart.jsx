import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { CLASSIFICATIONS } from "../../constants/classification";

export default function TimelineChart({ series = [] }) {
  const modelledLabels = Object.entries(CLASSIFICATIONS)
    .filter(([, meta]) => meta.modelled)
    .map(([label]) => label);

  const chartData = series.map((item) => {
    const row = { date: item.date };
    modelledLabels.forEach((label) => {
      row[label] = item.counts?.[label] || 0;
    });
    return row;
  });

  return (
    <div style={{ width: "100%", height: 320 }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E6ECF3" />
          <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#44566B" }} />
          <YAxis tick={{ fontSize: 11, fill: "#44566B" }} />
          <Tooltip
            contentStyle={{
              backgroundColor: "#FFFFFF",
              borderColor: "#D8E2EE",
              borderRadius: 8,
              boxShadow: "0 4px 12px rgba(27, 58, 92, 0.10)",
              fontSize: 12,
            }}
          />
          <Legend wrapperStyle={{ fontSize: 12, paddingTop: 10 }} />
          {modelledLabels.map((label) => (
            <Line
              key={label}
              type="monotone"
              dataKey={label}
              stroke={CLASSIFICATIONS[label].color}
              strokeWidth={2}
              dot={{ r: 3 }}
              activeDot={{ r: 6 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
