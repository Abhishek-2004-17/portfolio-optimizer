import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.models.ticker import Ticker
from app.services.ticker_service import TickerService

logger = logging.getLogger(__name__)


class TickerRepository:
    """Repository for managing ticker data in the database."""

    @staticmethod
    def get_or_fetch_tickers(
        db: Session, force_refresh: bool = False, cache_hours: int = 24
    ) -> list[dict]:
        """
        Get tickers from cache or fetch from sources.
        """
        # Check if we have cached data
        if not force_refresh:
            cached = db.query(Ticker).order_by(Ticker.symbol).all()
            if cached:
                # Check if cache is still valid
                if cached and cached[0].updated_at:
                    age = datetime.utcnow() - cached[0].updated_at
                    if age < timedelta(hours=cache_hours):
                        logger.info(f"Using cached tickers ({len(cached)} records)")
                        return [
                            {"symbol": t.symbol, "name": t.name, "sector": t.sector, "exchange": t.exchange}
                            for t in cached
                        ]

        # Fetch new data
        logger.info("Fetching fresh ticker data...")
        tickers = TickerService.fetch_all_tickers()

        # Clear old cache and store new data
        db.query(Ticker).delete()
        db.commit()

        for ticker in tickers:
            db_ticker = Ticker(
                symbol=ticker["symbol"],
                name=ticker.get("name", ""),
                sector=ticker.get("sector", ""),
                exchange=ticker.get("exchange", ""),
            )
            db.add(db_ticker)

        db.commit()

        return tickers

    @staticmethod
    def search_tickers(db: Session, query: str, limit: int = 50) -> list[dict]:
        """
        Search tickers by symbol or name.
        """
        if not query:
            return (
                db.query(Ticker)
                .order_by(Ticker.symbol)
                .limit(limit)
                .all()
            )

        q = f"%{query.upper()}%"

        # First try exact symbol match
        exact = db.query(Ticker).filter(Ticker.symbol == query.upper()).first()
        results = []
        if exact:
            results.append({"symbol": exact.symbol, "name": exact.name})

        # Then prefix matches
        prefix_matches = (
            db.query(Ticker)
            .filter(Ticker.symbol.ilike(f"{query.upper()}%"))
            .filter(Ticker.symbol != query.upper())
            .limit(limit)
            .all()
        )
        for t in prefix_matches:
            results.append({"symbol": t.symbol, "name": t.name})

        # Fill remaining with contains matches
        if len(results) < limit:
            remaining = limit - len(results)
            existing_symbols = {r["symbol"] for r in results}

            contains_matches = (
                db.query(Ticker)
                .filter(
                    (Ticker.symbol.ilike(q)) | (Ticker.name.ilike(q)),
                    ~Ticker.symbol.in_(existing_symbols),
                )
                .limit(remaining)
                .all()
            )
            for t in contains_matches:
                results.append({"symbol": t.symbol, "name": t.name})

        return results[:limit]

    @staticmethod
    def validate_ticker(db: Session, symbol: str) -> dict[str, Any]:
        """
        Validate a ticker symbol.
        Returns info if valid, None otherwise.
        """
        # Check database first
        cached = db.query(Ticker).filter(Ticker.symbol == symbol.upper()).first()
        if cached:
            return {"symbol": cached.symbol, "name": cached.name, "valid": True}

        # Validate with Yahoo Finance
        is_valid = TickerService.validate_ticker(symbol)

        if is_valid:
            # Cache the result
            ticker = Ticker(symbol=symbol.upper(), name="", exchange="YAHOO")
            db.add(ticker)
            db.commit()
            return {"symbol": symbol.upper(), "name": "Verified via Yahoo Finance", "valid": True}

        return {"symbol": symbol, "valid": False}
