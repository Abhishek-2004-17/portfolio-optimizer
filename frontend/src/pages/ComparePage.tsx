import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { EmptyState } from '@/components/ui/EmptyState';
import { AllocationPieChart } from '@/components/charts/AllocationPieChart';
import { WeightsBarChart } from '@/components/charts/WeightsBarChart';
import { listPortfolios } from '@/api/portfolioApi';

export function ComparePage() {
  const { data: portfolios } = useQuery({
    queryKey: ['portfolios'],
    queryFn: () => listPortfolios(),
  });

  const [leftId, setLeftId] = useState<number | null>(null);
  const [rightId, setRightId] = useState<number | null>(null);

  if (!portfolios || portfolios.length === 0) {
    return (
      <div className="space-y-6">
        <h2 className="text-2xl font-bold">Compare Portfolios</h2>
        <EmptyState
          title="No portfolios yet"
          description="Build and save portfolios to compare them side by side."
        />
      </div>
    );
  }

  const left = portfolios.find((p) => p.id === leftId) ?? portfolios[0];
  const right = portfolios.find((p) => p.id === rightId) ?? portfolios[1] ?? portfolios[0];

  const makeWeights = (p: typeof portfolios[0]) =>
    Object.fromEntries(p.assets.map((a) => [a.ticker, a.weight ?? 0]).filter(([, w]) => w > 0.001));

  const allTickers = Array.from(
    new Set([...left.assets, ...right.assets].map((a) => a.ticker))
  ).sort();

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Compare Portfolios</h2>

      {/* Selectors */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="text-xs text-muted block mb-1">Portfolio A</label>
          <select
            value={left.id}
            onChange={(e) => setLeftId(Number(e.target.value))}
            className="w-full bg-panel-light border border-panel-light rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-500"
          >
            {portfolios.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-xs text-muted block mb-1">Portfolio B</label>
          <select
            value={right.id}
            onChange={(e) => setRightId(Number(e.target.value))}
            className="w-full bg-panel-light border border-panel-light rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-500"
          >
            {portfolios.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Side-by-side cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {[left, right].map((p, idx) => (
          <div key={`${idx}-${p.id}`} className="bg-panel rounded-xl p-5 space-y-4">
            <div>
              <h3 className="font-semibold">{p.name}</h3>
              <p className="text-sm text-muted">
                {p.assets.length} assets |{' '}
                {p.initial_capital.toLocaleString('en-US', {
                  style: 'currency',
                  currency: 'USD',
                  maximumFractionDigits: 0,
                })}
              </p>
            </div>
            {Object.keys(makeWeights(p)).length > 0 && (
              <AllocationPieChart weights={makeWeights(p)} />
            )}
            {Object.keys(makeWeights(p)).length > 0 && (
              <WeightsBarChart weights={makeWeights(p)} />
            )}
          </div>
        ))}
      </div>

      {/* Weight comparison table */}
      {allTickers.length > 0 && (
        <div className="bg-panel rounded-xl p-5">
          <h3 className="font-semibold mb-3">Weight Comparison</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-panel-light">
                  <th className="text-left py-2 text-muted font-medium">Ticker</th>
                  <th className="text-right py-2 text-muted font-medium">{left.name}</th>
                  <th className="text-right py-2 text-muted font-medium">{right.name}</th>
                  <th className="text-right py-2 text-muted font-medium">Diff</th>
                </tr>
              </thead>
              <tbody>
                {allTickers.map((ticker) => {
                  const lw = left.assets.find((a) => a.ticker === ticker)?.weight ?? 0;
                  const rw = right.assets.find((a) => a.ticker === ticker)?.weight ?? 0;
                  const diff = lw - rw;
                  return (
                    <tr key={ticker} className="border-b border-panel-light/50">
                      <td className="py-2 font-medium">{ticker}</td>
                      <td className="text-right py-2">{(lw * 100).toFixed(1)}%</td>
                      <td className="text-right py-2">{(rw * 100).toFixed(1)}%</td>
                      <td className={`text-right py-2 ${diff > 0.001 ? 'text-bull' : diff < -0.001 ? 'text-bear' : 'text-muted'}`}>
                        {diff > 0 ? '+' : ''}{(diff * 100).toFixed(1)}%
                      </td>
                    </tr>
                  );
                })}
              </tbody>
              <tfoot>
                <tr className="font-medium">
                  <td className="py-2">Capital</td>
                  <td className="text-right py-2">
                    {left.initial_capital.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })}
                  </td>
                  <td className="text-right py-2">
                    {right.initial_capital.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })}
                  </td>
                  <td />
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
