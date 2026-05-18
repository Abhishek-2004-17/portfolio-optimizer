from pydantic import BaseModel, ConfigDict, Field


class OptimizeRequest(BaseModel):
    tickers: list[str] = Field(..., min_length=2, max_length=50)
    start_date: str
    end_date: str
    risk_free_rate: float = 0.04
    weight_bounds: tuple[float, float] = (0.0, 1.0)
    portfolio_id: int | None = None
    method: str = "max_sharpe"
    total_portfolio_value: float | None = None


class TargetRiskRequest(BaseModel):
    tickers: list[str] = Field(..., min_length=2, max_length=50)
    start_date: str
    end_date: str
    target_volatility: float = Field(..., gt=0)
    risk_free_rate: float = 0.04
    weight_bounds: tuple[float, float] = (0.0, 1.0)


class TargetReturnRequest(BaseModel):
    tickers: list[str] = Field(..., min_length=2, max_length=50)
    start_date: str
    end_date: str
    target_return: float
    risk_free_rate: float = 0.04
    weight_bounds: tuple[float, float] = (0.0, 1.0)


class FrontierRequest(BaseModel):
    tickers: list[str] = Field(..., min_length=2, max_length=50)
    start_date: str
    end_date: str
    risk_free_rate: float = 0.04
    weight_bounds: tuple[float, float] = (0.0, 1.0)
    n_points: int = Field(50, ge=10, le=200)
    total_portfolio_value: float | None = None


class OptimizeResponse(BaseModel):
    method: str
    weights: dict[str, float]
    expected_return: float
    volatility: float
    sharpe_ratio: float
    discrete_allocation: dict[str, int] | None = None
    leftover_cash: float | None = None


class FrontierPoint(BaseModel):
    volatility: float
    expected_return: float
    sharpe: float
    weights: dict[str, float]


class AssetPoint(BaseModel):
    ticker: str
    volatility: float
    expected_return: float


class FrontierResponse(BaseModel):
    points: list[FrontierPoint]
    max_sharpe: FrontierPoint
    min_vol: FrontierPoint
    asset_points: list[AssetPoint]
    latest_prices: dict[str, float] | None = None
