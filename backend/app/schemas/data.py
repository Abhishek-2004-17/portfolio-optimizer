from pydantic import BaseModel, Field


class HistoricalDataRequest(BaseModel):
    tickers: list[str] = Field(..., min_length=1, max_length=50)
    start_date: str
    end_date: str
    interval: str = "1d"


class OHLCVData(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    adj_close: float
    volume: int


class HistoricalDataResponse(BaseModel):
    ticker: str
    data: list[OHLCVData]


class QuoteResponse(BaseModel):
    ticker: str
    price: float
    change: float | None = None
    change_percent: float | None = None
    volume: int | None = None


class TickerSearchResult(BaseModel):
    symbol: str
    name: str
    exchange: str | None = None
