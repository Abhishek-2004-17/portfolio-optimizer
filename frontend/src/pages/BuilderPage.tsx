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
import { formatPercent, formatNumber } from '@/utils/format';
import { getEfficientFrontier } from '@/api/optimizationApi';
import { createPortfolio, addAsset } from '@/api/portfolioApi';
import { usePortfolioStore } from '@/store/portfolioStore';
import type { FrontierResponse, FrontierPoint } from '@/types/optimization';

const schema = z.object({
  tickers: z.array(z.object({ value: z.string().min(1, 'Ticker required') })).min(2, 'At least 2 tickers'),
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

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Build Portfolio</h2>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Form */}
        <div className="lg:col-span-1 space-y-4">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Tickers */}
            <div className="bg-panel rounded-xl p-4 space-y-3">
              <label className="text-sm font-medium text-muted block">Tickers</label>
              {fields.map((field, index) => (
                <div key={field.id} className="flex gap-2">
                  <input
                    {...register(`tickers.${index}.value`)}
                    className="flex-1 bg-panel-light border border-panel-light rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-500"
                    placeholder="e.g. AAPL"
                  />
                  {fields.length > 2 && (
                    <button
                      type="button"
                      onClick={() => remove(index)}
                      className="text-muted hover:text-bear transition-colors"
                    >
                      <Trash2 size={16} />
                    </button>
                  )}
                </div>
              ))}
              <button
                type="button"
                onClick={() => append({ value: '' })}
                className="flex items-center gap-1 text-brand-500 text-sm hover:underline"
              >
                <Plus size={14} /> Add ticker
              </button>
              {errors.tickers && <p className="text-bear text-xs">{errors.tickers.message}</p>}
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
              <div className="grid grid-cols-3 gap-3">
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
              <div>
                <label className="text-xs text-muted block mb-1">Capital ($)</label>
                <input
                  type="number"
                  value={saveCapital}
                  onChange={(e) => setSaveCapital(Number(e.target.value))}
                  className="w-full bg-panel-light border border-panel-light rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-500"
                />
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
