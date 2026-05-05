import numpy as np
import pandas as pd
import yfinance as yf
from scipy.stats import norm


class RiskService:
    @staticmethod
    def historical_var(port_returns: np.ndarray, confidence: float, pv: float = 1.0) -> tuple[float, float]:
        """Empirical quantile VaR and CVaR."""
        alpha = 1 - confidence
        var_pct = -np.quantile(port_returns, alpha)
        cvar_pct = -port_returns[port_returns <= -var_pct].mean() if np.any(port_returns <= -var_pct) else var_pct
        return float(var_pct * pv), float(cvar_pct * pv)

    @staticmethod
    def parametric_var(
        returns_df: pd.DataFrame, weights: np.ndarray, confidence: float, pv: float = 1.0
    ) -> tuple[float, float]:
        """Variance-covariance (parametric) VaR and CVaR assuming normality."""
        mu = returns_df.mean().values
        Sigma = returns_df.cov().values
        mu_p = float(weights @ mu)
        sigma_p = float(np.sqrt(weights @ Sigma @ weights))
        z = norm.ppf(confidence)
        var_pct = z * sigma_p - mu_p
        cvar_pct = sigma_p * norm.pdf(z) / (1 - confidence) - mu_p
        return float(var_pct * pv), float(cvar_pct * pv)

    @staticmethod
    def monte_carlo_var(
        returns_df: pd.DataFrame,
        weights: np.ndarray,
        confidence: float,
        pv: float = 1.0,
        n_sims: int = 10_000,
        horizon_days: int = 1,
        seed: int = 42,
    ) -> tuple[float, float]:
        """Monte Carlo VaR with Cholesky decomposition for correlated assets."""
        rng = np.random.default_rng(seed)
        mu = returns_df.mean().values
        Sigma = returns_df.cov().values
        L = np.linalg.cholesky(Sigma)

        mu_h = mu * horizon_days
        L_h = L * np.sqrt(horizon_days)

        Z = rng.standard_normal((n_sims, len(mu)))
        sim_rets = mu_h + Z @ L_h.T
        sim_port = sim_rets @ weights

        losses = -sim_port
        var = float(np.quantile(losses, confidence))
        cvar = float(losses[losses >= var].mean()) if np.any(losses >= var) else var
        return var * pv, cvar * pv

    @staticmethod
    def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.04, trading_days: int = 252) -> float:
        excess = returns - risk_free_rate / trading_days
        if returns.std() == 0:
            return 0.0
        return float(np.sqrt(trading_days) * excess.mean() / returns.std())

    @staticmethod
    def sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.04, trading_days: int = 252) -> float:
        excess = returns - risk_free_rate / trading_days
        downside = returns[returns < 0]
        if len(downside) == 0 or downside.std() == 0:
            return 0.0
        return float(np.sqrt(trading_days) * excess.mean() / downside.std())

    @staticmethod
    def compute_beta(port_returns: pd.Series, market_ticker: str = "SPY", trading_days: int = 252) -> float | None:
        """Compute portfolio beta against a market benchmark."""
        try:
            market_data = yf.download(
                market_ticker, period="5y", auto_adjust=True, progress=False
            )
            if market_data.empty:
                return None
            market_returns = market_data["Close"].pct_change().dropna()
            common_idx = port_returns.index.intersection(market_returns.index)
            if len(common_idx) < 30:
                return None
            pr = port_returns.loc[common_idx]
            mr = market_returns.loc[common_idx]
            cov_matrix = np.cov(pr.values, mr.values)
            market_var = cov_matrix[1, 1]
            if market_var == 0:
                return None
            return float(cov_matrix[0, 1] / market_var)
        except Exception:
            return None

    @staticmethod
    def max_drawdown(returns: pd.Series) -> tuple[float, pd.Series]:
        """Compute max drawdown (scalar) and drawdown series."""
        wealth = (1 + returns).cumprod()
        peak = wealth.cummax()
        dd = (wealth - peak) / peak
        return float(dd.min()), dd

    @staticmethod
    def correlation_matrix(returns_df: pd.DataFrame) -> dict[str, dict[str, float]]:
        """Compute Pearson correlation matrix as nested dict."""
        corr = returns_df.corr()
        return {col: {row: float(corr.loc[row, col]) for row in corr.index} for col in corr.columns}

    def compute_dashboard(
        self,
        tickers: list[str],
        weights: list[float],
        start_date: str,
        end_date: str,
        portfolio_value: float = 1_000_000,
        confidence_levels: list[float] | None = None,
        num_simulations: int = 10_000,
    ) -> dict:
        """Compute the full risk dashboard."""
        if confidence_levels is None:
            confidence_levels = [0.95, 0.99]

        prices = yf.download(tickers, start=start_date, end=end_date, auto_adjust=True, progress=False)
        if prices.empty:
            raise ValueError("No price data returned from Yahoo Finance")

        close = prices["Close"]
        if isinstance(close, pd.Series):
            close = close.to_frame(tickers[0])

        returns = close.pct_change().dropna()
        w = np.array(weights)
        w = w / w.sum()

        port_returns = returns.dot(w)

        # VaR and CVaR for each method × confidence level
        var_historical = {}
        var_parametric = {}
        var_montecarlo = {}
        cvar_historical = {}
        cvar_parametric = {}
        cvar_montecarlo = {}

        for cl in confidence_levels:
            label = f"{int(cl * 100)}"

            vh, cvh = self.historical_var(port_returns.values, cl, portfolio_value)
            var_historical[label] = vh
            cvar_historical[label] = cvh

            vp, cvp = self.parametric_var(returns, w, cl, portfolio_value)
            var_parametric[label] = vp
            cvar_parametric[label] = cvp

            vm, cvm = self.monte_carlo_var(
                returns, w, cl, portfolio_value, num_simulations
            )
            var_montecarlo[label] = vm
            cvar_montecarlo[label] = cvm

        # Other metrics
        sharpe = self.sharpe_ratio(port_returns)
        sortino = self.sortino_ratio(port_returns)
        beta = self.compute_beta(port_returns)
        max_dd, dd_series = self.max_drawdown(port_returns)
        corr = self.correlation_matrix(returns)

        # Annualized metrics
        ann_return = float(port_returns.mean() * 252)
        ann_vol = float(port_returns.std() * np.sqrt(252))

        return {
            "var_historical": var_historical,
            "var_parametric": var_parametric,
            "var_montecarlo": var_montecarlo,
            "cvar_historical": cvar_historical,
            "cvar_parametric": cvar_parametric,
            "cvar_montecarlo": cvar_montecarlo,
            "sharpe": sharpe,
            "sortino": sortino,
            "beta": beta,
            "max_drawdown": max_dd,
            "correlation_matrix": corr,
            "annualised_return": ann_return,
            "annualised_volatility": ann_vol,
        }
