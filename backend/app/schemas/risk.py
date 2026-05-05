from pydantic import BaseModel, Field


class RiskRequest(BaseModel):
    tickers: list[str] = Field(..., min_length=1, max_length=50)
    weights: list[float] = Field(..., min_length=1)
    start_date: str
    end_date: str
    portfolio_value: float = 1_000_000
    confidence_levels: list[float] = [0.95, 0.99]
    num_simulations: int = 10_000
    horizon_days: int = 1


class RiskDashboardRequest(BaseModel):
    tickers: list[str] = Field(..., min_length=1, max_length=50)
    weights: list[float] = Field(..., min_length=1)
    start_date: str
    end_date: str
    portfolio_value: float = 1_000_000


class VaRResult(BaseModel):
    method: str
    confidence: float
    var_value: float
    cvar_value: float


class DrawdownResult(BaseModel):
    max_drawdown: float
    recovery_days: int | None
    series: list[dict[str, float]]


class RiskDashboardResponse(BaseModel):
    var_historical: dict[str, float]
    var_parametric: dict[str, float]
    var_montecarlo: dict[str, float]
    cvar_historical: dict[str, float]
    cvar_parametric: dict[str, float]
    cvar_montecarlo: dict[str, float]
    sharpe: float
    sortino: float
    beta: float | None
    max_drawdown: float
    correlation_matrix: dict[str, dict[str, float]]
    annualised_return: float
    annualised_volatility: float
