import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.data import (
    HistoricalDataRequest,
    HistoricalDataResponse,
    OHLCVData,
    QuoteResponse,
    TickerSearchResult,
)
from app.services.data_service import DataService

router = APIRouter()


@router.post("/historical", response_model=list[HistoricalDataResponse])
def fetch_historical(body: HistoricalDataRequest, db: Session = Depends(get_db)):
    start_date = dt.date.fromisoformat(body.start_date)
    end_date = dt.date.fromisoformat(body.end_date)

    data = DataService.fetch_historical(
        db,
        tickers=body.tickers,
        start_date=start_date,
        end_date=end_date,
        interval=body.interval,
    )

    responses: list[HistoricalDataResponse] = []
    for ticker, df in data.items():
        ohlcv_list = [
            OHLCVData(
                date=str(row["date"]),
                open=row["open"],
                high=row["high"],
                low=row["low"],
                close=row["close"],
                adj_close=row["adj_close"],
                volume=int(row["volume"]),
            )
            for _idx, row in df.iterrows()
        ]
        responses.append(HistoricalDataResponse(ticker=ticker, data=ohlcv_list))

    return responses


@router.get("/quote/{ticker}", response_model=QuoteResponse)
def get_quote(ticker: str):
    quote = DataService.get_latest_quote(ticker)
    if quote is None:
        raise HTTPException(status_code=404, detail=f"Quote not found for ticker: {ticker}")
    return QuoteResponse(**quote)


@router.get("/validate/{ticker}")
def validate_ticker(ticker: str):
    valid = DataService.validate_ticker(ticker)
    return {"valid": valid}


@router.get("/search", response_model=list[TickerSearchResult])
def search_tickers(q: str = Query(..., min_length=1)):
    results = DataService.search_tickers(q)
    return [TickerSearchResult(**r) for r in results]


@router.get("/tickers", response_model=list[str])
def get_cached_tickers(db: Session = Depends(get_db)):
    return DataService.get_cached_tickers(db)
