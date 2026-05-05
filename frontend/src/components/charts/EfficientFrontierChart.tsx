import {
  ScatterChart, Scatter, XAxis, YAxis, ZAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceDot, Legend,
} from 'recharts';
import type { FrontierResponse } from '@/types/optimization';

interface Props {
  result: FrontierResponse;
}

export function EfficientFrontierChart({ result }: Props) {
  const frontier = result.points.map((f) => ({ x: f.volatility, y: f.expected_return }));
  const assets = result.asset_points.map((a) => ({ x: a.volatility, y: a.expected_return, ticker: a.ticker }));

  return (
    <div className="h-96 rounded-xl bg-panel p-4">
      <h3 className="text-sm font-medium text-muted mb-3">Efficient Frontier</h3>
      <ResponsiveContainer width="100%" height="90%">
        <ScatterChart>
          <CartesianGrid stroke="#1e293b" />
          <XAxis type="number" dataKey="x" tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} name="Volatility" />
          <YAxis type="number" dataKey="y" tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} name="Return" />
          <ZAxis range={[40, 40]} />
          <Tooltip
            formatter={(v: number, name: string) => [`${(v * 100).toFixed(2)}%`, name === 'x' ? 'Volatility' : 'Return']}
          />
          <Legend />
          <Scatter name="Frontier" data={frontier} fill="#0ea5e9" line shape="circle" />
          <Scatter name="Individual Assets" data={assets} fill="#f59e0b" shape="triangle" />
          <ReferenceDot
            x={result.max_sharpe.volatility}
            y={result.max_sharpe.expected_return}
            r={8}
            fill="#10b981"
            label={{ value: 'Max Sharpe', position: 'top', fill: '#10b981', fontSize: 11 }}
          />
          <ReferenceDot
            x={result.min_vol.volatility}
            y={result.min_vol.expected_return}
            r={8}
            fill="#a855f7"
            label={{ value: 'Min Vol', position: 'bottom', fill: '#a855f7', fontSize: 11 }}
          />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
