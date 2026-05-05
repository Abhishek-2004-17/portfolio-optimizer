import { TrendingUp, TrendingDown, Activity, BarChart3 } from 'lucide-react';
import { StatCard } from '@/components/ui/StatCard';
import { formatPercent } from '@/utils/format';
import type { RiskDashboardResponse } from '@/types/risk';

interface Props {
  data: RiskDashboardResponse;
}

export function RiskMetricsDashboard({ data }: Props) {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
      <StatCard
        label="Sharpe Ratio"
        value={data.sharpe.toFixed(2)}
        icon={<Activity size={16} />}
        trend={data.sharpe > 0 ? 'up' : 'down'}
      />
      <StatCard
        label="Sortino Ratio"
        value={data.sortino.toFixed(2)}
        icon={<TrendingUp size={16} />}
        trend={data.sortino > 0 ? 'up' : 'down'}
      />
      <StatCard
        label="Max Drawdown"
        value={formatPercent(data.max_drawdown)}
        icon={<TrendingDown size={16} />}
        trend="down"
      />
      <StatCard
        label="Beta"
        value={data.beta?.toFixed(2) ?? '--'}
        icon={<BarChart3 size={16} />}
      />
      <StatCard
        label="Annualised Return"
        value={formatPercent(data.annualised_return)}
        trend={data.annualised_return > 0 ? 'up' : 'down'}
      />
      <StatCard
        label="Annualised Volatility"
        value={formatPercent(data.annualised_volatility)}
      />
    </div>
  );
}
