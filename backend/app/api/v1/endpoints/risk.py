from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.risk_metric import RiskMetric
from app.repositories.risk_repo import RiskMetricRepository
from app.schemas.risk import RiskDashboardRequest, RiskDashboardResponse, RiskRequest
from app.services.risk_service import RiskService

router = APIRouter()
risk_service = RiskService()


@router.post("/var")
def compute_var(body: RiskRequest, db: Session = Depends(get_db)):
    import numpy as np
    import pandas as pd
    import yfinance as yf

    prices = yf.download(body.tickers, start=body.start_date, end=body.end_date, auto_adjust=True, progress=False)
    close = prices["Close"]
    if isinstance(close, pd.Series):
        close = close.to_frame(body.tickers[0])
    returns = close.pct_change().dropna()
    w = np.array(body.weights)
    w = w / w.sum()
    port_returns = returns.dot(w)

    results = {}
    for cl in body.confidence_levels:
        label = f"{int(cl * 100)}"
        vh, _ = risk_service.historical_var(port_returns.values, cl, body.portfolio_value)
        vp, _ = risk_service.parametric_var(returns, w, cl, body.portfolio_value)
        vm, _ = risk_service.monte_carlo_var(returns, w, cl, body.portfolio_value, body.num_simulations)
        results[label] = {"historical": vh, "parametric": vp, "montecarlo": vm}
    return results


@router.post("/cvar")
def compute_cvar(body: RiskRequest, db: Session = Depends(get_db)):
    import numpy as np
    import pandas as pd
    import yfinance as yf

    prices = yf.download(body.tickers, start=body.start_date, end=body.end_date, auto_adjust=True, progress=False)
    close = prices["Close"]
    if isinstance(close, pd.Series):
        close = close.to_frame(body.tickers[0])
    returns = close.pct_change().dropna()
    w = np.array(body.weights)
    w = w / w.sum()
    port_returns = returns.dot(w)

    results = {}
    for cl in body.confidence_levels:
        label = f"{int(cl * 100)}"
        _, cvh = risk_service.historical_var(port_returns.values, cl, body.portfolio_value)
        _, cvp = risk_service.parametric_var(returns, w, cl, body.portfolio_value)
        _, cvm = risk_service.monte_carlo_var(returns, w, cl, body.portfolio_value, body.num_simulations)
        results[label] = {"historical": cvh, "parametric": cvp, "montecarlo": cvm}
    return results


@router.post("/correlation")
def compute_correlation(body: RiskRequest, db: Session = Depends(get_db)):
    import pandas as pd
    import yfinance as yf

    prices = yf.download(body.tickers, start=body.start_date, end=body.end_date, auto_adjust=True, progress=False)
    close = prices["Close"]
    if isinstance(close, pd.Series):
        close = close.to_frame(body.tickers[0])
    returns = close.pct_change().dropna()
    return risk_service.correlation_matrix(returns)


@router.post("/drawdown")
def compute_drawdown(body: RiskRequest, db: Session = Depends(get_db)):
    import numpy as np
    import pandas as pd
    import yfinance as yf

    prices = yf.download(body.tickers, start=body.start_date, end=body.end_date, auto_adjust=True, progress=False)
    close = prices["Close"]
    if isinstance(close, pd.Series):
        close = close.to_frame(body.tickers[0])
    returns = close.pct_change().dropna()
    w = np.array(body.weights)
    w = w / w.sum()
    port_returns = returns.dot(w)

    max_dd, dd_series = risk_service.max_drawdown(port_returns)
    series_data = [{"date": str(d.date()), "drawdown": float(v)} for d, v in dd_series.items()]

    # Estimate recovery days
    dd_values = dd_series.values
    trough_idx = np.argmin(dd_values)
    post_trough = dd_values[trough_idx:]
    recovery_idx = np.where(post_trough >= -0.001)[0]
    recovery_days = int(recovery_idx[0]) if len(recovery_idx) > 0 else None

    return {"max_drawdown": max_dd, "recovery_days": recovery_days, "series": series_data}


@router.post("/sharpe")
def compute_sharpe(body: RiskRequest, db: Session = Depends(get_db)):
    import numpy as np
    import pandas as pd
    import yfinance as yf

    prices = yf.download(body.tickers, start=body.start_date, end=body.end_date, auto_adjust=True, progress=False)
    close = prices["Close"]
    if isinstance(close, pd.Series):
        close = close.to_frame(body.tickers[0])
    returns = close.pct_change().dropna()
    w = np.array(body.weights)
    w = w / w.sum()
    port_returns = returns.dot(w)
    return {"sharpe": risk_service.sharpe_ratio(port_returns)}


@router.post("/sortino")
def compute_sortino(body: RiskRequest, db: Session = Depends(get_db)):
    import numpy as np
    import pandas as pd
    import yfinance as yf

    prices = yf.download(body.tickers, start=body.start_date, end=body.end_date, auto_adjust=True, progress=False)
    close = prices["Close"]
    if isinstance(close, pd.Series):
        close = close.to_frame(body.tickers[0])
    returns = close.pct_change().dropna()
    w = np.array(body.weights)
    w = w / w.sum()
    port_returns = returns.dot(w)
    return {"sortino": risk_service.sortino_ratio(port_returns)}


@router.post("/beta")
def compute_beta(body: RiskRequest, db: Session = Depends(get_db)):
    import numpy as np
    import pandas as pd
    import yfinance as yf

    prices = yf.download(body.tickers, start=body.start_date, end=body.end_date, auto_adjust=True, progress=False)
    close = prices["Close"]
    if isinstance(close, pd.Series):
        close = close.to_frame(body.tickers[0])
    returns = close.pct_change().dropna()
    w = np.array(body.weights)
    w = w / w.sum()
    port_returns = returns.dot(w)
    return {"beta": risk_service.compute_beta(port_returns)}


@router.post("/dashboard", response_model=RiskDashboardResponse)
def compute_dashboard(body: RiskDashboardRequest, db: Session = Depends(get_db)):
    dashboard = risk_service.compute_dashboard(
        tickers=body.tickers,
        weights=body.weights,
        start_date=body.start_date,
        end_date=body.end_date,
        portfolio_value=body.portfolio_value,
    )
    return dashboard


@router.get("/portfolio/{portfolio_id}/latest", response_model=RiskDashboardResponse)
def get_latest_risk(portfolio_id: int, db: Session = Depends(get_db)):
    metric = RiskMetricRepository.get_latest_for_portfolio(db, portfolio_id)
    if not metric:
        raise HTTPException(status_code=404, detail="No risk metrics found for this portfolio")

    return RiskDashboardResponse(
        var_historical={"95": metric.var_historical_95 or 0, "99": metric.var_historical_99 or 0},
        var_parametric={"95": metric.var_parametric_95 or 0, "99": metric.var_parametric_99 or 0},
        var_montecarlo={"95": metric.var_montecarlo_95 or 0, "99": metric.var_montecarlo_99 or 0},
        cvar_historical={"95": metric.cvar_historical_95 or 0, "99": metric.cvar_historical_99 or 0},
        cvar_parametric={"95": metric.cvar_parametric_95 or 0, "99": metric.cvar_parametric_99 or 0},
        cvar_montecarlo={"95": metric.cvar_montecarlo_95 or 0, "99": metric.cvar_montecarlo_99 or 0},
        sharpe=metric.sharpe_ratio or 0,
        sortino=metric.sortino_ratio or 0,
        beta=metric.beta,
        max_drawdown=metric.max_drawdown or 0,
        correlation_matrix=metric.correlation_matrix or {},
        annualised_return=metric.annualised_return or 0,
        annualised_volatility=metric.annualised_volatility or 0,
    )
