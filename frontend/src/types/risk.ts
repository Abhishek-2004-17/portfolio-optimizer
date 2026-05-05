export interface RiskDashboardRequest {
  tickers: string[];
  weights: number[];
  start_date: string;
  end_date: string;
  portfolio_value?: number;
}

export interface RiskDashboardResponse {
  var_historical: Record<string, number>;
  var_parametric: Record<string, number>;
  var_montecarlo: Record<string, number>;
  cvar_historical: Record<string, number>;
  cvar_parametric: Record<string, number>;
  cvar_montecarlo: Record<string, number>;
  sharpe: number;
  sortino: number;
  beta: number | null;
  max_drawdown: number;
  correlation_matrix: Record<string, Record<string, number>>;
  annualised_return: number;
  annualised_volatility: number;
}
