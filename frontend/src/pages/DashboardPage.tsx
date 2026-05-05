import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Briefcase, TrendingUp, Plus, Trash2 } from 'lucide-react';
import { toast } from 'sonner';
import { StatCard } from '@/components/ui/StatCard';
import { AllocationPieChart } from '@/components/charts/AllocationPieChart';
import { listPortfolios, deletePortfolio } from '@/api/portfolioApi';
import { usePortfolioStore } from '@/store/portfolioStore';
import { formatPercent, formatNumber } from '@/utils/format';
import { CHART_COLORS } from '@/utils/colors';

export function DashboardPage() {
  const { lastOptimization, lastFrontier } = usePortfolioStore();
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const { data: portfolios, isLoading, refetch } = useQuery({
    queryKey: ['portfolios'],
    queryFn: () => listPortfolios(),
  });
  const opt = lastOptimization ?? lastFrontier?.max_sharpe ?? null;
  const sharpe = opt ? ('sharpe_ratio' in opt ? opt.sharpe_ratio : (opt as any).sharpe) : null;

  const handleDelete = async (id: number, name: string) => {
    setDeletingId(id);
    try {
      await deletePortfolio(id);
      toast.success(`"${name}" deleted`);
      refetch();
    } catch (e: any) {
      toast.error(e.message || 'Delete failed');
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Dashboard</h2>
        <Link
          to="/build"
          className="flex items-center gap-2 bg-brand-500 hover:bg-brand-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          <Plus size={16} />
          New Portfolio
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Total Portfolios"
          value={portfolios?.length ?? 0}
          icon={<Briefcase size={16} />}
        />
        <StatCard
          label="Total Value"
          value={
            portfolios
              ?.reduce((sum, p) => sum + p.initial_capital, 0)
              .toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }) ?? '$0'
          }
        />
        <StatCard
          label="Expected Return"
          value={opt ? formatPercent(opt.expected_return) : '--'}
          trend={opt && opt.expected_return > 0 ? 'up' : undefined}
          icon={<TrendingUp size={16} />}
        />
        <StatCard
          label="Sharpe Ratio"
          value={sharpe != null ? formatNumber(sharpe) : '--'}
          trend={sharpe != null && sharpe > 0 ? 'up' : undefined}
        />
      </div>

      {isLoading && <div className="animate-pulse h-48 bg-panel-light rounded-xl" />}

      {portfolios && portfolios.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Saved Portfolios</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {portfolios.map((p) => {
              const weights = Object.fromEntries(
                p.assets.map((a) => [a.ticker, a.weight ?? 0]).filter(([, w]) => w > 0.001)
              );
              const totalWeight = Object.values(weights).reduce((a, b) => a + b, 0);
              const date = new Date(p.created_at).toLocaleDateString();

              return (
                <div
                  key={p.id}
                  className="bg-panel border border-panel-light rounded-xl p-5 space-y-3 hover:border-brand-500/50 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-semibold">{p.name}</h4>
                      <p className="text-xs text-muted mt-0.5">{date}</p>
                    </div>
                    <button
                      onClick={() => handleDelete(p.id, p.name)}
                      disabled={deletingId === p.id}
                      className="text-muted hover:text-bear transition-colors p-1"
                      title="Delete portfolio"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>

                  <div className="flex items-center gap-3 text-xs text-muted">
                    <span>{p.assets.length} assets</span>
                    <span>|</span>
                    <span>
                      {p.initial_capital.toLocaleString('en-US', {
                        style: 'currency',
                        currency: 'USD',
                        maximumFractionDigits: 0,
                      })}
                    </span>
                  </div>

                  {/* Allocation bar */}
                  {Object.keys(weights).length > 0 && (
                    <div>
                      <div className="flex h-3 rounded-full overflow-hidden">
                        {p.assets.map((a, i) => {
                          const w = a.weight ?? 0;
                          if (w < 0.001) return null;
                          return (
                            <div
                              key={a.ticker}
                              className="h-full transition-all"
                              style={{
                                width: `${(w / totalWeight) * 100}%`,
                                backgroundColor: CHART_COLORS[i % CHART_COLORS.length],
                              }}
                              title={`${a.ticker}: ${(w * 100).toFixed(1)}%`}
                            />
                          );
                        })}
                      </div>
                      <div className="flex flex-wrap gap-x-3 gap-y-1 mt-2">
                        {p.assets.map((a, i) => {
                          const w = a.weight ?? 0;
                          if (w < 0.001) return null;
                          return (
                            <span key={a.ticker} className="text-[10px] text-muted flex items-center gap-1">
                              <span
                                className="w-2 h-2 rounded-full inline-block"
                                style={{ backgroundColor: CHART_COLORS[i % CHART_COLORS.length] }}
                              />
                              {a.ticker} {(w * 100).toFixed(0)}%
                            </span>
                          );
                        })}
                      </div>
                    </div>
                  )}

                  {/* Mini pie chart */}
                  {Object.keys(weights).length > 0 && (
                    <div className="h-32">
                      <AllocationPieChart weights={weights} />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {portfolios && portfolios.length === 0 && (
        <div className="border-2 border-dashed border-panel-light rounded-xl p-16 text-center">
          <h3 className="text-muted text-lg mb-2">No portfolios yet</h3>
          <p className="text-muted/60 text-sm mb-4">Build your first optimized portfolio to get started</p>
          <Link
            to="/build"
            className="inline-flex items-center gap-2 bg-brand-500 hover:bg-brand-600 text-white px-6 py-2.5 rounded-lg text-sm font-medium transition-colors"
          >
            <Plus size={16} />
            Build Portfolio
          </Link>
        </div>
      )}
    </div>
  );
}
