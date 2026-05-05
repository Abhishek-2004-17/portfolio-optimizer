import { formatCurrency } from '@/utils/format';
import type { RiskDashboardResponse } from '@/types/risk';

interface Props {
  data: RiskDashboardResponse;
  portfolioValue: number;
}

const methods = [
  { key: 'historical', label: 'Historical Simulation' },
  { key: 'parametric', label: 'Parametric (Variance-Covariance)' },
  { key: 'montecarlo', label: 'Monte Carlo (Cholesky)' },
] as const;

const levels = ['95', '99'] as const;

export function VaRDisplay({ data, portfolioValue }: Props) {
  return (
    <div className="rounded-xl bg-panel p-4 overflow-auto">
      <h3 className="text-sm font-medium text-muted mb-4">Value-at-Risk Comparison</h3>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-panel-light">
            <th className="text-left py-2 pr-4 text-muted font-medium">Method</th>
            {levels.map((l) => (
              <th key={l} className="text-right py-2 px-4 text-muted font-medium">VaR {l}%</th>
            ))}
            {levels.map((l) => (
              <th key={`cvar-${l}`} className="text-right py-2 px-4 text-muted font-medium">CVaR {l}%</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {methods.map(({ key, label }) => (
            <tr key={key} className="border-b border-panel-light/50">
              <td className="py-3 pr-4 font-medium">{label}</td>
              {levels.map((l) => (
                <td key={`var-${l}`} className="text-right py-3 px-4 text-bear">
                  {formatCurrency((data as any)[`var_${key}`]?.[l] ?? 0)}
                </td>
              ))}
              {levels.map((l) => (
                <td key={`cvar-${l}`} className="text-right py-3 px-4 text-bear/70">
                  {formatCurrency((data as any)[`cvar_${key}`]?.[l] ?? 0)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
