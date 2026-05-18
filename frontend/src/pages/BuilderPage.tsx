import { useMemo, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { toast } from 'sonner';
import { Plus, Trash2, Play, Save } from 'lucide-react';

import { EfficientFrontierChart } from '@/components/charts/EfficientFrontierChart';
import { AllocationPieChart } from '@/components/charts/AllocationPieChart';
import { WeightsBarChart } from '@/components/charts/WeightsBarChart';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ErrorPanel } from '@/components/ui/ErrorPanel';
import { StatCard } from '@/components/ui/StatCard';
import { TickerInput } from '@/components/ui/TickerInput';
import { formatPercent, formatNumber } from '@/utils/format';
import { getEfficientFrontier } from '@/api/optimizationApi';
import { createPortfolio, addAsset } from '@/api/portfolioApi';
import { usePortfolioStore } from '@/store/portfolioStore';
import type { FrontierResponse, FrontierPoint } from '@/types/optimization';

const schema = z.object({
  tickers: z.array(z.object({ value: z.string().min(1, 'Ticker required') })).min(1, 'At least 1 ticker').max(50, 'Maximum 50 tickers'),
  start_date: z.string().min(1),
  end_date: z.string().min(1),
  risk_free_rate: z.number().min(0).max(1),
  weight_bounds_min: z.number().min(-1).max(2),
  weight_bounds_max: z.number().min(-1).max(2),
});

type FormData = z.infer<typeof schema>;

function interpolateFrontier(
  frontier: FrontierResponse,
  slider: number,
): FrontierPoint {
  const sorted = [...frontier.points].sort((a, b) => a.volatility - b.volatility);
  if (sorted.length === 0) return frontier.max_sharpe;

  const minV = sorted[0].volatility;
  const maxV = sorted[sorted.length - 1].volatility;
  const target = minV + slider * (maxV - minV);

  // Find the two bracketing points
  let lo = sorted[0];
  let hi = sorted[sorted.length - 1];
  for (let i = 0; i < sorted.length - 1; i++) {
    if (sorted[i].volatility <= target && sorted[i + 1].volatility >= target) {
      lo = sorted[i];
      hi = sorted[i + 1];
      break;
    }
  }

  // Linear interpolation
  const range = hi.volatility - lo.volatility;
  const t = range === 0 ? 0 : (target - lo.volatility) / range;

  const tickers = Object.keys(lo.weights);
  const interpWeights: Record<string, number> = {};
  for (const tk of tickers) {
    interpWeights[tk] = (lo.weights[tk] ?? 0) * (1 - t) + (hi.weights[tk] ?? 0) * t;
  }

  return {
    volatility: lo.volatility * (1 - t) + hi.volatility * t,
    expected_return: lo.expected_return * (1 - t) + hi.expected_return * t,
    sharpe: lo.sharpe * (1 - t) + hi.sharpe * t,
    weights: interpWeights,
  };
}

export function BuilderPage() {
  const { setLastFrontier, setLastOptimization } = usePortfolioStore();
  const [frontier, setFrontier] = useState<FrontierResponse | null>(null);
  const [riskTolerance, setRiskTolerance] = useState(0.5);
  const [saveCapital, setSaveCapital] = useState(100000);

  const {
    register,
    control,
    handleSubmit,
    setValue,
    getValues,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      tickers: [{ value: 'AAPL' }, { value: 'MSFT' }, { value: 'GOOGL' }],
      start_date: new Date(new Date().setFullYear(new Date().getFullYear() - 3)).toISOString().slice(0, 10),
      end_date: new Date().toISOString().slice(0, 10),
      risk_free_rate: 0.04,
      weight_bounds_min: 0,
      weight_bounds_max: 1,
    },
  });

  const { fields, append, remove } = useFieldArray({ control, name: 'tickers' });

  const frontierMutation = useMutation({
    mutationFn: (data: FormData) =>
      getEfficientFrontier({
        tickers: data.tickers.map((t) => t.value.toUpperCase()),
        start_date: data.start_date,
        end_date: data.end_date,
        risk_free_rate: data.risk_free_rate,
        weight_bounds: [data.weight_bounds_min, data.weight_bounds_max],
        total_portfolio_value: saveCapital,
      }),
    onSuccess: (data) => {
      setFrontier(data);
      setLastFrontier(data);
      setRiskTolerance(0.5);
      toast.success('Efficient frontier computed');
    },
    onError: (err) => toast.error(err.message),
  });

  const saveMutation = useMutation({
    mutationFn: async (data: { name: string; weights: Record<string, number>; capital: number }) => {
      const portfolio = await createPortfolio({ name: data.name, initial_capital: data.capital });
      for (const [ticker, weight] of Object.entries(data.weights)) {
        if (weight > 0.001) {
          await addAsset(portfolio.id, { ticker, weight });
        }
      }
      return portfolio;
    },
    onSuccess: () => toast.success('Portfolio saved'),
    onError: (err) => toast.error(err.message),
  });

  const onSubmit = (data: FormData) => {
    frontierMutation.mutate(data);
  };

  // Interpolate current portfolio from slider position + frontier data
  const sliderPoint = useMemo(() => {
    if (!frontier) return null;
    return interpolateFrontier(frontier, riskTolerance);
  }, [frontier, riskTolerance]);

  const currentOpt = sliderPoint ?? (frontier ? frontier.max_sharpe : null);
  const displayWeights = currentOpt?.weights ?? {};

  // Calculate discrete allocation (shares to buy) from weights and prices
  const discreteAllocation = useMemo(() => {
    if (!currentOpt?.weights || !frontier?.latest_prices || saveCapital <= 0) {
      return null;
    }
    const prices = frontier.latest_prices;
    const weights = currentOpt.weights;
    const allocation: Record<string, { shares: number; amount: number; price: number }> = {};
    let totalInvested = 0;

    for (const [ticker, weight] of Object.entries(weights)) {
      if (weight > 0.001 && prices[ticker]) {
        const targetAmount = saveCapital * weight;
        const shares = Math.floor(targetAmount / prices[ticker]);
        const amount = shares * prices[ticker];
        if (shares > 0) {
          allocation[ticker] = {
            shares,
            amount,
            price: prices[ticker],
          };
          totalInvested += amount;
        }
      }
    }

    return {
      allocation,
      totalInvested,
      leftoverCash: saveCapital - totalInvested,
    };
  }, [currentOpt, frontier, saveCapital]);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Build Portfolio</h2>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Form */}
        <div className="lg:col-span-1 space-y-4">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Tickers */}
            <div className="bg-panel rounded-xl p-4 space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-muted block">Tickers</label>
                <span className="text-xs text-muted">{fields.length} / 50</span>
              </div>
              {fields.map((field, index) => (
                <div key={field.id} className="flex gap-2">
                  <TickerInput
                    value={field.value}
                    onChange={(val) => {
                      // Update the form value
                      const tickers = getValues().tickers;
                      const updated = [...tickers];
                      updated[index] = { value: val };
                      setValue('tickers', updated);
                    }}
                  />
                  <button
                    type="button"
                    onClick={() => remove(index)}
                    className="text-muted hover:text-bear transition-colors mt-1"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              ))}
              {fields.length < 50 && (
                <button
                  type="button"
                  onClick={() => append({ value: '' })}
                  className="flex items-center gap-1 text-brand-500 text-sm hover:underline"
                >
                  <Plus size={14} /> Add ticker
                </button>
              )}
              {errors.tickers && <p className="text-bear text-xs">{errors.tickers.message}</p>}
              <p className="text-xs text-muted">
                Search from 100+ popular stocks, ETFs, or enter any ticker manually
              </p>
            </div>

            {/* Date range */}
            <div className="bg-panel rounded-xl p-4 space-y-3">
              <label className="text-sm font-medium text-muted block">Date Range</label>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-muted">Start</label>
                  <input
                    type="date"
                    {...register('start_date')}
                    className="w-full bg-panel-light border border-panel-light rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-500"
                  />
                </div>
                <div>
                  <label className="text-xs text-muted">End</label>
                  <input
                    type="date"
                    {...register('end_date')}
                    className="w-full bg-panel-light border border-panel-light rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-500"
                  />
                </div>
              </div>
            </div>

            {/* Parameters */}
            <div className="bg-panel rounded-xl p-4 space-y-3">
              <label className="text-sm font-medium text-muted block">Parameters</label>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-muted">Risk-free rate</label>
                  <input
                    type="number"
                    step="0.01"
                    {...register('risk_free_rate', { valueAsNumber: true })}
                    className="w-full bg-panel-light border border-panel-light rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-500"
                  />
                </div>
                <div>
                  <label className="text-xs text-muted">Capital ($)</label>
                  <input
                    type="number"
                    step="1000"
                    min="1000"
                    value={saveCapital}
                    onChange={(e) => setSaveCapital(Number(e.target.value))}
                    className="w-full bg-panel-light border border-panel-light rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-500"
                  />
                </div>
                <div>
                  <label className="text-xs text-muted">Min weight</label>
                  <input
                    type="number"
                    step="0.1"
                    {...register('weight_bounds_min', { valueAsNumber: true })}
                    className="w-full bg-panel-light border border-panel-light rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-500"
                  />
                </div>
                <div>
                  <label className="text-xs text-muted">Max weight</label>
                  <input
                    type="number"
                    step="0.1"
                    {...register('weight_bounds_max', { valueAsNumber: true })}
                    className="w-full bg-panel-light border border-panel-light rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-500"
                  />
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={frontierMutation.isPending}
              className="w-full flex items-center justify-center gap-2 bg-brand-500 hover:bg-brand-600 disabled:opacity-50 text-white py-2.5 rounded-lg text-sm font-medium transition-colors"
            >
              <Play size={16} />
              {frontierMutation.isPending ? 'Computing...' : 'Run Optimization'}
            </button>
          </form>

          {/* Risk slider — interpolates frontier data locally, no API calls */}
          {frontier && (
            <div className="bg-panel rounded-xl p-4 space-y-3">
              <label className="text-sm font-medium text-muted block">Risk Tolerance</label>
              <div className="flex items-center justify-between text-xs text-muted mb-1">
                <span>Conservative</span>
                <span>Vol: {formatPercent(currentOpt?.volatility)}</span>
                <span>Aggressive</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.005"
                value={riskTolerance}
                onChange={(e) => {
                  setRiskTolerance(parseFloat(e.target.value));
                }}
                className="w-full accent-brand-500"
              />
              <div className="flex justify-between text-[10px] text-muted">
                <span>Return: {formatPercent(frontier.min_vol.expected_return)}</span>
                <span>Return: {formatPercent(frontier.points[frontier.points.length - 1]?.expected_return)}</span>
              </div>
            </div>
          )}

          {/* Save section */}
          {currentOpt && (
            <div className="bg-panel rounded-xl p-4 space-y-3">
              <div>
                <label className="text-xs text-muted block mb-1">Portfolio Name</label>
                <input
                  type="text"
                  defaultValue={`Portfolio ${new Date().toLocaleDateString()}`}
                  id="portfolio-name"
                  className="w-full bg-panel-light border border-panel-light rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-500"
                />
              </div>
              <div className="text-xs text-muted">
                Saving with capital: ${saveCapital.toLocaleString()}
              </div>
              <button
                onClick={() => {
                  const nameInput = document.getElementById('portfolio-name') as HTMLInputElement;
                  saveMutation.mutate({
                    name: nameInput?.value || `Portfolio ${Date.now()}`,
                    weights: currentOpt.weights,
                    capital: saveCapital,
                  });
                }}
                disabled={saveMutation.isPending}
                className="w-full flex items-center justify-center gap-2 bg-bull/20 hover:bg-bull/30 text-bull py-2.5 rounded-lg text-sm font-medium transition-colors"
              >
                <Save size={16} />
                {saveMutation.isPending ? 'Saving...' : 'Save Portfolio'}
              </button>
            </div>
          )}
        </div>

        {/* Results */}
        <div className="lg:col-span-2 space-y-6">
          {frontierMutation.isPending && <LoadingSpinner />}
          {frontierMutation.error && (
            <ErrorPanel message={frontierMutation.error.message} onRetry={() => frontierMutation.reset()} />
          )}

          {currentOpt && (
            <div className="grid grid-cols-3 gap-4">
              <StatCard label="Expected Return" value={formatPercent(currentOpt.expected_return)} trend="up" />
              <StatCard label="Volatility" value={formatPercent(currentOpt.volatility)} />
              <StatCard label="Sharpe Ratio" value={formatNumber(currentOpt.sharpe)} trend={currentOpt.sharpe > 0 ? 'up' : 'down'} />
            </div>
          )}

          {/* Discrete Allocation */}
          {discreteAllocation && (
            <div className="bg-panel rounded-xl p-4 space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-medium text-muted">Discrete Allocation</h3>
                <span className="text-xs text-muted">Capital: ${saveCapital.toLocaleString()}</span>
              </div>
              <div className="space-y-2">
                {Object.entries(discreteAllocation.allocation).map(([ticker, data]) => (
                  <div key={ticker} className="flex items-center justify-between text-sm py-2 border-b border-panel-light">
                    <div className="flex items-center gap-2 flex-1">
                      <span className="font-medium">{ticker}</span>
                      <span className="text-muted text-xs">{displayWeights[ticker] ? `${(displayWeights[ticker] * 100).toFixed(1)}%` : ''}</span>
                    </div>
                    <div className="flex items-center gap-4 text-right">
                      <span className="font-mono text-brand-400">{data.shares} shares</span>
                      <span className="text-muted text-xs">@ ${data.price.toFixed(2)}</span>
                      <span className="font-mono w-24">${data.amount.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}</span>
                    </div>
                  </div>
                ))}
              </div>
              <div className="flex justify-between text-xs text-muted pt-2 border-t border-panel-light">
                <span>Total invested: ${discreteAllocation.totalInvested.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}</span>
                <span className="text-bull">Cash leftover: ${discreteAllocation.leftoverCash.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}</span>
              </div>
            </div>
          )}

          {frontier && <EfficientFrontierChart result={frontier} />}

          {Object.keys(displayWeights).length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <AllocationPieChart weights={displayWeights} />
              <WeightsBarChart weights={displayWeights} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
