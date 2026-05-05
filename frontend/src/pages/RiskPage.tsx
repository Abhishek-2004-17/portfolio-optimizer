import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { toast } from 'sonner';
import { ShieldAlert } from 'lucide-react';

import { RiskMetricsDashboard } from '@/components/charts/RiskMetricsDashboard';
import { VaRDisplay } from '@/components/charts/VaRDisplay';
import { CorrelationMatrix } from '@/components/charts/CorrelationMatrix';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ErrorPanel } from '@/components/ui/ErrorPanel';
import { EmptyState } from '@/components/ui/EmptyState';
import { computeDashboard } from '@/api/riskApi';
import { usePortfolioStore } from '@/store/portfolioStore';
import type { RiskDashboardResponse } from '@/types/risk';

export function RiskPage() {
  const { lastFrontier, lastOptimization, dateRange } = usePortfolioStore();
  const [result, setResult] = useState<RiskDashboardResponse | null>(null);
  const [startDate, setStartDate] = useState(dateRange.start);
  const [endDate, setEndDate] = useState(dateRange.end);
  const [portfolioValue, setPortfolioValue] = useState(1_000_000);

  const tickers = lastOptimization
    ? Object.keys(lastOptimization.weights)
    : lastFrontier
      ? Object.keys(lastFrontier.max_sharpe.weights)
      : [];

  const weights = lastOptimization
    ? Object.values(lastOptimization.weights)
    : lastFrontier
      ? Object.values(lastFrontier.max_sharpe.weights)
      : [];

  const mutation = useMutation({
    mutationFn: () =>
      computeDashboard({
        tickers,
        weights,
        start_date: startDate,
        end_date: endDate,
        portfolio_value: portfolioValue,
      }),
    onSuccess: (data) => {
      setResult(data);
      toast.success('Risk analysis complete');
    },
    onError: (err) => toast.error(err.message),
  });

  if (tickers.length === 0) {
    return (
      <div className="space-y-6">
        <h2 className="text-2xl font-bold">Risk Analysis</h2>
        <EmptyState
          title="No portfolio to analyze"
          description="Build and optimize a portfolio first, then return here for risk analysis."
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Risk Analysis</h2>
        <button
          onClick={() => mutation.mutate()}
          disabled={mutation.isPending}
          className="flex items-center gap-2 bg-brand-500 hover:bg-brand-600 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          <ShieldAlert size={16} />
          {mutation.isPending ? 'Analyzing...' : 'Run Analysis'}
        </button>
      </div>

      {/* Configuration panel */}
      <div className="bg-panel rounded-xl p-4 space-y-4">
        <p className="text-sm text-muted">
          Analyzing: <span className="text-slate-100 font-medium">{tickers.join(', ')}</span>
          {' '}({weights.length} assets)
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div>
            <label className="text-xs text-muted block mb-1">Start Date</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full bg-panel-light border border-panel-light rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-500"
            />
          </div>
          <div>
            <label className="text-xs text-muted block mb-1">End Date</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full bg-panel-light border border-panel-light rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-500"
            />
          </div>
          <div>
            <label className="text-xs text-muted block mb-1">Portfolio Value ($)</label>
            <input
              type="number"
              value={portfolioValue}
              onChange={(e) => setPortfolioValue(Number(e.target.value))}
              className="w-full bg-panel-light border border-panel-light rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-500"
            />
          </div>
        </div>
      </div>

      {mutation.isPending && <LoadingSpinner />}
      {mutation.error && (
        <ErrorPanel message={mutation.error.message} onRetry={() => mutation.mutate()} />
      )}

      {result && (
        <>
          <RiskMetricsDashboard data={result} />
          <VaRDisplay data={result} portfolioValue={portfolioValue} />
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <CorrelationMatrix tickers={tickers} matrix={result.correlation_matrix} />
          </div>
        </>
      )}

      {!result && !mutation.isPending && !mutation.error && (
        <EmptyState
          title="Ready to analyze"
          description="Click 'Run Analysis' to compute VaR, CVaR, Sharpe, Sortino, and more."
        />
      )}
    </div>
  );
}
