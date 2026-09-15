import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";

export default function ClassificationPie({ breakdown = [] }) {
  const activeData = breakdown.filter((item) => item.count > 0);

  return (
    <div style={{ width: "100%", height: 300 }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={activeData}
            dataKey="count"
            nameKey="label"
            cx="50%"
            cy="50%"
            outerRadius={95}
            innerRadius={45}
            paddingAngle={3}
            label={({ label, percentage }) => `${percentage}%`}
            labelLine={false}
          >
            {activeData.map((entry) => (
              <Cell key={entry.label} fill={entry.color} stroke="#FFFFFF" strokeWidth={2} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value, name) => [`${value.toLocaleString()} events`, name]}
            contentStyle={{
              backgroundColor: "#FFFFFF",
              borderColor: "#D8E2EE",
              borderRadius: 8,
              fontSize: 12,
            }}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
