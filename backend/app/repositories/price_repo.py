import datetime as dt

import pandas as pd
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.models.price_history import PriceHistory


class PriceHistoryRepository:
    @staticmethod
    def get_by_ticker_range(
        db: Session,
        ticker: str,
        start_date: dt.date,
        end_date: dt.date,
    ) -> list[PriceHistory]:
        """Get cached prices for a ticker in a date range, ordered by date."""
        stmt = (
            select(PriceHistory)
            .where(
                PriceHistory.ticker == ticker,
                PriceHistory.date >= start_date,
                PriceHistory.date <= end_date,
            )
            .order_by(PriceHistory.date)
        )
        return list(db.scalars(stmt).all())

    @staticmethod
    def upsert_prices(db: Session, ticker: str, df: pd.DataFrame) -> int:
        """Bulk upsert price data from a pandas DataFrame.

        Uses PostgreSQL INSERT ... ON CONFLICT DO UPDATE for efficiency.
        Expects DataFrame with columns: date, open, high, low, close, adj_close, volume.
        Returns the number of rows upserted.
        """
        if df.empty:
            return 0

        table = PriceHistory.__table__
        rows = []
        for _idx, row in df.iterrows():
            rows.append(
                {
                    "ticker": ticker,
                    "date": row["date"].date() if hasattr(row["date"], "date") else row["date"],
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "adj_close": float(row["adj_close"]),
                    "volume": int(row["volume"]),
                }
            )

        stmt = pg_insert(table).values(rows)
        stmt = stmt.on_conflict_do_update(
            constraint="price_history_ticker_date_key",
            set_={
                "open": stmt.excluded.open,
                "high": stmt.excluded.high,
                "low": stmt.excluded.low,
                "close": stmt.excluded.close,
                "adj_close": stmt.excluded.adj_close,
                "volume": stmt.excluded.volume,
            },
        )
        result = db.execute(stmt)
        db.commit()
        return result.rowcount

    @staticmethod
    def get_cached_tickers(db: Session) -> list[str]:
        """List distinct tickers in the price_history table."""
        stmt = select(PriceHistory.ticker).distinct().order_by(PriceHistory.ticker)
        return list(db.scalars(stmt).all())

    @staticmethod
    def get_missing_ranges(
        db: Session,
        ticker: str,
        start_date: dt.date,
        end_date: dt.date,
    ) -> list[tuple[dt.date, dt.date]]:
        """Find date gaps that need to be fetched.

        Compares the set of trading dates present in the DB for the given
        ticker+range against a continuous calendar. Returns contiguous
        blocks of missing dates as (start, end) pairs.

        For simplicity and performance with potentially large ranges, we
        fetch the distinct dates already cached and compute missing spans.
        """
        # Get all cached dates for this ticker in the range
        stmt = (
            select(PriceHistory.date)
            .where(
                PriceHistory.ticker == ticker,
                PriceHistory.date >= start_date,
                PriceHistory.date <= end_date,
            )
            .order_by(PriceHistory.date)
        )
        cached_dates = set(db.scalars(stmt).all())

        if not cached_dates:
            return [(start_date, end_date)]

        # Walk the calendar and find contiguous missing ranges
        missing_ranges: list[tuple[dt.date, dt.date]] = []
        range_start = None

        current = start_date
        while current <= end_date:
            if current not in cached_dates:
                if range_start is None:
                    range_start = current
            else:
                if range_start is not None:
                    missing_ranges.append((range_start, current - dt.timedelta(days=1)))
                    range_start = None
            current += dt.timedelta(days=1)

        # Close any open range at the end
        if range_start is not None:
            missing_ranges.append((range_start, end_date))

        return missing_ranges
