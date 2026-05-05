import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

interface DrawdownPoint {
  date: string;
  drawdown: number;
}

interface Props {
  series: DrawdownPoint[];
}

export function DrawdownChart({ series }: Props) {
  const data = series.map((d) => ({ ...d, drawdown: d.drawdown * 100 }));

  return (
    <div className="h-64 rounded-xl bg-panel p-4">
      <h3 className="text-sm font-medium text-muted mb-3">Drawdown</h3>
      <ResponsiveContainer width="100%" height="85%">
        <AreaChart data={data}>
          <defs>
            <linearGradient id="ddGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#ef4444" stopOpacity={0.3} />
              <stop offset="100%" stopColor="#ef4444" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis dataKey="date" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
          <YAxis tickFormatter={(v) => `${v}%`} tick={{ fontSize: 10 }} />
          <Tooltip formatter={(v: number) => `${v.toFixed(2)}%`} />
          <Area type="monotone" dataKey="drawdown" stroke="#ef4444" fill="url(#ddGrad)" isAnimationActive={false} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
