import logging

import numpy as np
import pandas as pd
import yfinance as yf
from pypfopt import EfficientFrontier, objective_functions
from pypfopt.discrete_allocation import DiscreteAllocation
from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import CovarianceShrinkage

logger = logging.getLogger(__name__)


class OptimizationService:
    @staticmethod
    def _make_ef(
        mu: pd.Series,
        sigma: pd.DataFrame,
        weight_bounds: tuple[float, float] = (0.0, 1.0),
        gamma: float = 0.1,
        add_l2_reg: bool = True,
    ) -> EfficientFrontier:
        try:
            ef = EfficientFrontier(mu, sigma, weight_bounds=weight_bounds)
            if add_l2_reg:
                ef.add_objective(objective_functions.L2_reg, gamma=gamma)
            return ef
        except Exception:
            ef = EfficientFrontier(mu, sigma, weight_bounds=(0.0, 1.0))
            if add_l2_reg:
                ef.add_objective(objective_functions.L2_reg, gamma=gamma * 0.5)
            return ef

    @staticmethod
    def _download_prices(
        tickers: list[str], start_date: str, end_date: str
    ) -> pd.DataFrame:
        prices = yf.download(
            tickers, start=start_date, end=end_date, auto_adjust=True,
            progress=False, threads=False,
        )
        if prices.empty:
            raise ValueError("No price data returned for the given tickers and dates")

        # Handle MultiIndex columns from yfinance
        close = prices["Close"]
        if isinstance(close, pd.DataFrame):
            close = close.dropna(axis=1, how="all").dropna()
        elif isinstance(close, pd.Series):
            close = close.to_frame(name=tickers[0]).dropna()

        if close.empty:
            raise ValueError("No price data returned for the given tickers and dates")

        # Only keep tickers that actually have data
        available = [t for t in tickers if t in close.columns]
        if len(available) < len(tickers):
            import logging
            logging.getLogger(__name__).warning(
                "Missing data for tickers: %s", [t for t in tickers if t not in available]
            )
        return close[available]

    @staticmethod
    def _compute_mu_sigma(prices_df: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
        mu = mean_historical_return(prices_df, frequency=252)
        sigma = CovarianceShrinkage(prices_df).ledoit_wolf()
        return mu, sigma

    @staticmethod
    def max_sharpe(
        tickers: list[str],
        start_date: str,
        end_date: str,
        risk_free_rate: float = 0.04,
        weight_bounds: tuple[float, float] = (0.0, 1.0),
        total_portfolio_value: float | None = None,
    ) -> dict:
        prices = OptimizationService._download_prices(tickers, start_date, end_date)
        mu, sigma = OptimizationService._compute_mu_sigma(prices)

        ef = OptimizationService._make_ef(mu, sigma, weight_bounds, add_l2_reg=False)
        ef.max_sharpe(risk_free_rate=risk_free_rate)
        clean_weights = ef.clean_weights(cutoff=1e-6)
        performance = ef.portfolio_performance(risk_free_rate=risk_free_rate)

        discrete_allocation = None
        leftover_cash = None
        if total_portfolio_value is not None:
            latest_prices = prices.iloc[-1]
            da = DiscreteAllocation(
                clean_weights,
                latest_prices,
                total_portfolio_value=total_portfolio_value,
            )
            alloc, leftover = da.lp_portfolio()
            discrete_allocation = {k: int(v) for k, v in alloc.items()}
            leftover_cash = float(leftover)

        return {
            "method": "max_sharpe",
            "weights": {k: float(v) for k, v in clean_weights.items()},
            "expected_return": float(performance[0]),
            "volatility": float(performance[1]),
            "sharpe_ratio": float(performance[2]),
            "discrete_allocation": discrete_allocation,
            "leftover_cash": leftover_cash,
        }

    @staticmethod
    def min_volatility(
        tickers: list[str],
        start_date: str,
        end_date: str,
        weight_bounds: tuple[float, float] = (0.0, 1.0),
    ) -> dict:
        prices = OptimizationService._download_prices(tickers, start_date, end_date)
        mu, sigma = OptimizationService._compute_mu_sigma(prices)

        ef = OptimizationService._make_ef(mu, sigma, weight_bounds)
        ef.min_volatility()
        clean_weights = ef.clean_weights(cutoff=1e-6)
        performance = ef.portfolio_performance()

        return {
            "method": "min_volatility",
            "weights": {k: float(v) for k, v in clean_weights.items()},
            "expected_return": float(performance[0]),
            "volatility": float(performance[1]),
            "sharpe_ratio": float(performance[2]),
            "discrete_allocation": None,
            "leftover_cash": None,
        }

    @staticmethod
    def target_return(
        tickers: list[str],
        start_date: str,
        end_date: str,
        target_return: float,
        risk_free_rate: float = 0.04,
        weight_bounds: tuple[float, float] = (0.0, 1.0),
    ) -> dict:
        prices = OptimizationService._download_prices(tickers, start_date, end_date)
        mu, sigma = OptimizationService._compute_mu_sigma(prices)

        ef = OptimizationService._make_ef(mu, sigma, weight_bounds)
        ef.efficient_return(target_return=target_return)
        clean_weights = ef.clean_weights(cutoff=1e-6)
        performance = ef.portfolio_performance(risk_free_rate=risk_free_rate)

        return {
            "method": "target_return",
            "weights": {k: float(v) for k, v in clean_weights.items()},
            "expected_return": float(performance[0]),
            "volatility": float(performance[1]),
            "sharpe_ratio": float(performance[2]),
            "discrete_allocation": None,
            "leftover_cash": None,
        }

    @staticmethod
    def target_risk(
        tickers: list[str],
        start_date: str,
        end_date: str,
        target_volatility: float,
        risk_free_rate: float = 0.04,
        weight_bounds: tuple[float, float] = (0.0, 1.0),
    ) -> dict:
        prices = OptimizationService._download_prices(tickers, start_date, end_date)
        mu, sigma = OptimizationService._compute_mu_sigma(prices)

        ef = OptimizationService._make_ef(mu, sigma, weight_bounds)
        ef.efficient_risk(target_volatility=target_volatility)
        clean_weights = ef.clean_weights(cutoff=1e-6)
        performance = ef.portfolio_performance(risk_free_rate=risk_free_rate)

        return {
            "method": "target_risk",
            "weights": {k: float(v) for k, v in clean_weights.items()},
            "expected_return": float(performance[0]),
            "volatility": float(performance[1]),
            "sharpe_ratio": float(performance[2]),
            "discrete_allocation": None,
            "leftover_cash": None,
        }

    @staticmethod
    def efficient_frontier(
        tickers: list[str],
        start_date: str,
        end_date: str,
        risk_free_rate: float = 0.04,
        weight_bounds: tuple[float, float] = (0.0, 1.0),
        n_points: int = 50,
        total_portfolio_value: float | None = None,
    ) -> dict:
        prices = OptimizationService._download_prices(tickers, start_date, end_date)
        available_tickers = list(prices.columns)
        mu, sigma = OptimizationService._compute_mu_sigma(prices)

        # Get latest prices for discrete allocation
        latest_prices = prices.iloc[-1]

        # Compute min-volatility portfolio
        ef_min = OptimizationService._make_ef(mu, sigma, weight_bounds)
        try:
            ef_min.min_volatility()
        except Exception:
            ef_min = EfficientFrontier(mu, sigma, weight_bounds=(0.0, 1.0))
            ef_min.min_volatility()
        min_vol_weights = ef_min.clean_weights(cutoff=1e-6)
        min_vol_perf = ef_min.portfolio_performance(risk_free_rate=risk_free_rate)
        min_vol_point = {
            "volatility": float(min_vol_perf[1]),
            "expected_return": float(min_vol_perf[0]),
            "sharpe": float(min_vol_perf[2]),
            "weights": {k: float(v) for k, v in min_vol_weights.items()},
        }

        # Compute max-Sharpe portfolio
        ef_max = OptimizationService._make_ef(mu, sigma, weight_bounds, add_l2_reg=False)
        try:
            ef_max.max_sharpe(risk_free_rate=risk_free_rate)
        except Exception:
            ef_max = EfficientFrontier(mu, sigma, weight_bounds=(0.0, 1.0))
            ef_max.max_sharpe(risk_free_rate=risk_free_rate)
        max_sharpe_weights = ef_max.clean_weights(cutoff=1e-6)
        max_sharpe_perf = ef_max.portfolio_performance(risk_free_rate=risk_free_rate)
        max_sharpe_point = {
            "volatility": float(max_sharpe_perf[1]),
            "expected_return": float(max_sharpe_perf[0]),
            "sharpe": float(max_sharpe_perf[2]),
            "weights": {k: float(v) for k, v in max_sharpe_weights.items()},
        }

        # Generate frontier points
        min_vol = min_vol_point["volatility"]
        max_sharpe_vol = max_sharpe_point["volatility"]
        upper_vol = max_sharpe_vol * 1.4
        target_vols = np.linspace(min_vol, upper_vol, n_points).tolist()

        frontier_points = []
        for tv in target_vols:
            ef = OptimizationService._make_ef(mu, sigma, weight_bounds)
            try:
                ef.efficient_risk(target_volatility=tv)
                weights = ef.clean_weights(cutoff=1e-6)
                perf = ef.portfolio_performance(risk_free_rate=risk_free_rate)
                frontier_points.append(
                    {
                        "volatility": float(perf[1]),
                        "expected_return": float(perf[0]),
                        "sharpe": float(perf[2]),
                        "weights": {k: float(v) for k, v in weights.items()},
                    }
                )
            except Exception:
                continue

        # Compute individual asset points (only for tickers with data)
        asset_points = []
        for ticker in available_tickers:
            asset_vol = float(np.sqrt(sigma.loc[ticker, ticker]) * np.sqrt(252))
            asset_ret = float(mu[ticker])
            asset_points.append(
                {
                    "ticker": ticker,
                    "volatility": asset_vol,
                    "expected_return": asset_ret,
                }
            )

        return {
            "points": frontier_points,
            "max_sharpe": max_sharpe_point,
            "min_vol": min_vol_point,
            "asset_points": asset_points,
            "latest_prices": {k: float(v) for k, v in latest_prices.items()},
        }
