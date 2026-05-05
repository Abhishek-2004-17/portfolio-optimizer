import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { CHART_COLORS } from '@/utils/colors';

interface Props {
  weights: Record<string, number>;
}

export function AllocationPieChart({ weights }: Props) {
  const data = Object.entries(weights)
    .filter(([, v]) => v > 0.001)
    .map(([name, value]) => ({ name, value: parseFloat((value * 100).toFixed(1)) }));

  return (
    <div className="h-80 rounded-xl bg-panel p-4">
      <h3 className="text-sm font-medium text-muted mb-3">Allocation</h3>
      <ResponsiveContainer width="100%" height="90%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
            paddingAngle={2}
            dataKey="value"
            label={({ name, value }) => `${name}: ${value}%`}
          >
            {data.map((_, i) => (
              <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(v: number) => `${v}%`} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
