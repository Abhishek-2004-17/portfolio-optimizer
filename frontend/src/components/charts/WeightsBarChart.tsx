import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';
import { getColor } from '@/utils/colors';

interface Props {
  weights: Record<string, number>;
}

export function WeightsBarChart({ weights }: Props) {
  const data = Object.entries(weights)
    .filter(([, v]) => v > 0.001)
    .sort((a, b) => b[1] - a[1])
    .map(([ticker, weight], i) => ({ ticker, weight: parseFloat((weight * 100).toFixed(1)), fill: getColor(i) }));

  return (
    <div className="h-64 rounded-xl bg-panel p-4">
      <h3 className="text-sm font-medium text-muted mb-3">Weights</h3>
      <ResponsiveContainer width="100%" height="85%">
        <BarChart data={data} layout="vertical" margin={{ left: 60 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis type="number" tickFormatter={(v) => `${v}%`} />
          <YAxis dataKey="ticker" type="category" width={50} />
          <Tooltip formatter={(v: number) => `${v}%`} />
          <Bar dataKey="weight" radius={[0, 4, 4, 0]} isAnimationActive={false}>
            {data.map((entry, i) => (
              <Cell key={i} fill={entry.fill} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
