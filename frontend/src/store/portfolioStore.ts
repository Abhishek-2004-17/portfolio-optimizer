import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { OptimizeResponse, FrontierResponse } from '@/types/optimization';

interface DateRange {
  start: string;
  end: string;
}

interface PortfolioState {
  tickers: string[];
  dateRange: DateRange;
  riskTolerance: number;
  riskFreeRate: number;
  lastOptimization: OptimizeResponse | null;
  lastFrontier: FrontierResponse | null;
  setTickers: (t: string[]) => void;
  setDateRange: (d: DateRange) => void;
  setRiskTolerance: (v: number) => void;
  setLastOptimization: (o: OptimizeResponse | null) => void;
  setLastFrontier: (f: FrontierResponse | null) => void;
  reset: () => void;
}

function getDefaultDates() {
  const now = new Date();
  const end = now.toISOString().slice(0, 10);
  const start = new Date(now.getFullYear() - 3, now.getMonth(), now.getDate()).toISOString().slice(0, 10);
  return { start, end };
}

const initialState = {
  tickers: [],
  dateRange: getDefaultDates(),
  riskTolerance: 0.5,
  riskFreeRate: 0.04,
  lastOptimization: null,
  lastFrontier: null,
};

export const usePortfolioStore = create<PortfolioState>()(
  devtools(
    persist(
      (set) => ({
        ...initialState,
        setTickers: (tickers) => set({ tickers }),
        setDateRange: (dateRange) => set({ dateRange }),
        setRiskTolerance: (riskTolerance) => set({ riskTolerance }),
        setLastOptimization: (lastOptimization) => set({ lastOptimization }),
        setLastFrontier: (lastFrontier) => set({ lastFrontier }),
        reset: () => set(initialState),
      }),
      { name: 'portfolio-v1' },
    ),
  ),
);
