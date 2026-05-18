from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Any

from app.api.deps import get_db
from app.repositories.ticker_repo import TickerRepository
from app.schemas.ticker import TickerSearchResponse, TickerValidateResponse

router = APIRouter()


@router.get("/search", response_model=TickerSearchResponse)
def search_tickers(
    q: str = Query("", description="Search query (symbol or name)"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    db: Session = Depends(get_db),
) -> Any:
    """
    Search for tickers by symbol or company name.

    Results are ranked by:
    1. Exact symbol match
    2. Symbol prefix match
    3. Symbol contains match
    4. Company name contains match
    """
    try:
        tickers = TickerRepository.get_or_fetch_tickers(db)
        results = TickerRepository.search_tickers(db, q, limit)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/validate/{symbol}", response_model=TickerValidateResponse)
def validate_ticker(
    symbol: str,
    db: Session = Depends(get_db),
) -> Any:
    """
    Validate if a ticker symbol exists.

    Checks both local cache and Yahoo Finance.
    """
    result = TickerRepository.validate_ticker(db, symbol)

    if not result.get("valid"):
        raise HTTPException(
            status_code=404,
            detail=f"Ticker '{symbol}' not found on Yahoo Finance"
        )

    return result


@router.post("/refresh")
def refresh_ticker_cache(
    force: bool = Query(False, description="Force refresh even if cache is valid"),
    db: Session = Depends(get_db),
) -> Any:
    """
    Refresh the ticker cache from external sources.

    This fetches tickers from:
    - S&P 500 companies (Wikipedia)
    - NASDAQ-100 companies (Wikipedia)
    - Dow Jones Industrial Average (Wikipedia)
    - Popular ETFs
    - Popular stocks by sector

    Then validates each ticker against Yahoo Finance.
    """
    try:
        tickers = TickerRepository.get_or_fetch_tickers(db, force_refresh=force)
        return {
            "message": f"Successfully refreshed {len(tickers)} tickers",
            "count": len(tickers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refresh failed: {str(e)}")


@router.get("/stats")
def get_ticker_stats(db: Session = Depends(get_db)) -> Any:
    """
    Get statistics about the ticker database.
    """
    from app.models.ticker import Ticker
    from sqlalchemy import func

    total = db.query(func.count(Ticker.id)).scalar()
    from app.models.ticker import Ticker

    # Count by exchange
    exchange_counts = (
        db.query(Ticker.exchange, func.count(Ticker.id))
        .group_by(Ticker.exchange)
        .all()
    )

    # Get last update time
    latest = db.query(func.max(Ticker.updated_at)).scalar()

    return {
        "total_tickers": total,
        "by_exchange": {e or "Unknown": c for e, c in exchange_counts},
        "last_updated": latest.isoformat() if latest else None,
    }
