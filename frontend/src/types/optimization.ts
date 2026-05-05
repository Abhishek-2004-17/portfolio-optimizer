export interface OptimizeRequest {
  tickers: string[];
  start_date: string;
  end_date: string;
  risk_free_rate?: number;
  weight_bounds?: [number, number];
  portfolio_id?: number;
  method?: string;
  total_portfolio_value?: number;
}

export interface TargetRiskRequest {
  tickers: string[];
  start_date: string;
  end_date: string;
  target_volatility: number;
  risk_free_rate?: number;
  weight_bounds?: [number, number];
}

export interface OptimizeResponse {
  method: string;
  weights: Record<string, number>;
  expected_return: number;
  volatility: number;
  sharpe_ratio: number;
  discrete_allocation: Record<string, number> | null;
  leftover_cash: number | null;
}

export interface FrontierPoint {
  volatility: number;
  expected_return: number;
  sharpe: number;
  weights: Record<string, number>;
}

export interface AssetPoint {
  ticker: string;
  volatility: number;
  expected_return: number;
}

export interface FrontierResponse {
  points: FrontierPoint[];
  max_sharpe: FrontierPoint;
  min_vol: FrontierPoint;
  asset_points: AssetPoint[];
}
