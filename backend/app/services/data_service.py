import datetime as dt
import logging

import pandas as pd
import yfinance as yf
from sqlalchemy.orm import Session

from app.repositories.price_repo import PriceHistoryRepository

logger = logging.getLogger(__name__)


class DataService:
    """Cache-first data fetching service using yfinance backed by a PostgreSQL store."""

    # ------------------------------------------------------------------
    # Historical data (cache-first)
    # ------------------------------------------------------------------

    @staticmethod
    def fetch_historical(
        db: Session,
        tickers: list[str],
        start_date: dt.date,
        end_date: dt.date,
        interval: str = "1d",
    ) -> dict[str, pd.DataFrame]:
        """Fetch historical OHLCV data with a cache-first strategy.

        For each ticker:
          1. Identify missing date ranges via the repository.
          2. Fetch only the gaps from Yahoo Finance.
          3. Upsert the freshly fetched data into the DB.
          4. Return the complete cached dataset.

        Returns a dict mapping ticker -> DataFrame.
        """
        results: dict[str, pd.DataFrame] = {}

        for ticker in tickers:
            # Determine what we already have
            missing_ranges = PriceHistoryRepository.get_missing_ranges(
                db, ticker, start_date, end_date
            )

            # Fetch each missing range from yfinance and persist
            for gap_start, gap_end in missing_ranges:
                df = DataService._download_yfinance(ticker, gap_start, gap_end, interval)
                if df is not None and not df.empty:
                    PriceHistoryRepository.upsert_prices(db, ticker, df)
                    logger.info(
                        "Fetched & cached %d rows for %s (%s -> %s)",
                        len(df),
                        ticker,
                        gap_start,
                        gap_end,
                    )

            # Load the now-complete range from the DB
            cached = PriceHistoryRepository.get_by_ticker_range(db, ticker, start_date, end_date)
            if cached:
                rows = [
                    {
                        "date": r.date,
                        "open": float(r.open),
                        "high": float(r.high),
                        "low": float(r.low),
                        "close": float(r.close),
                        "adj_close": float(r.adj_close),
                        "volume": int(r.volume),
                    }
                    for r in cached
                ]
                results[ticker] = pd.DataFrame(rows)
            else:
                results[ticker] = pd.DataFrame()

        return results

    # ------------------------------------------------------------------
    # Real-time quote
    # ------------------------------------------------------------------

    @staticmethod
    def get_latest_quote(ticker: str) -> dict | None:
        """Retrieve a real-time quote for a single ticker via yfinance fast_info.

        Returns a dict matching the QuoteResponse schema, or None on failure.
        """
        try:
            t = yf.Ticker(ticker)
            info = t.fast_info

            price = getattr(info, "last_price", None)
            prev_close = getattr(info, "previous_close", None)

            if price is None:
                return None

            change = None
            change_percent = None
            if prev_close and prev_close != 0:
                change = round(price - prev_close, 4)
                change_percent = round((change / prev_close) * 100, 4)

            volume = getattr(info, "last_volume", None)

            return {
                "ticker": ticker,
                "price": round(price, 4),
                "change": change,
                "change_percent": change_percent,
                "volume": int(volume) if volume else None,
            }
        except Exception as exc:
            logger.warning("Failed to fetch quote for %s: %s", ticker, exc)
            return None

    # ------------------------------------------------------------------
    # Ticker validation
    # ------------------------------------------------------------------

    @staticmethod
    def validate_ticker(ticker: str) -> bool:
        """Check whether a ticker exists on Yahoo Finance."""
        try:
            t = yf.Ticker(ticker)
            # fast_info raises or returns None-like for invalid tickers
            info = t.fast_info
            last_price = getattr(info, "last_price", None)
            return last_price is not None
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Ticker search
    # ------------------------------------------------------------------

    @staticmethod
    def search_tickers(query: str) -> list[dict]:
        """Autocomplete search using yfinance / Yahoo Finance search endpoint.

        Returns a list of dicts matching TickerSearchResult schema.
        """
        try:
            # yfinance >= 0.2 exposes a Search class; fall back to Ticker info
            # approach: download a small batch to see what resolves
            results: list[dict] = []

            # Use yfinance's internal search via the downloaded module
            try:
                from yfinance import Search

                search = Search(query, max_results=10)
                for item in search.quotes:
                    results.append(
                        {
                            "symbol": item.get("symbol", ""),
                            "name": item.get("shortname", item.get("longname", "")),
                            "exchange": item.get("exchange", ""),
                        }
                    )
            except (ImportError, AttributeError):
                # Fallback: use Yahoo Finance search API directly
                import requests

                url = "https://query1.finance.yahoo.com/v1/finance/search"
                params = {"q": query, "quotes_count": 10, "news_count": 0}
                headers = {"User-Agent": "Mozilla/5.0"}
                resp = requests.get(url, params=params, headers=headers, timeout=5)
                resp.raise_for_status()
                data = resp.json()
                for item in data.get("quotes", []):
                    results.append(
                        {
                            "symbol": item.get("symbol", ""),
                            "name": item.get("shortname", item.get("longname", "")),
                            "exchange": item.get("exchange", ""),
                        }
                    )

            return results
        except Exception as exc:
            logger.warning("Ticker search failed for '%s': %s", query, exc)
            return []

    # ------------------------------------------------------------------
    # Cached tickers
    # ------------------------------------------------------------------

    @staticmethod
    def get_cached_tickers(db: Session) -> list[str]:
        """List all tickers that have data in the price_history table."""
        return PriceHistoryRepository.get_cached_tickers(db)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _download_yfinance(
        ticker: str,
        start: dt.date,
        end: dt.date,
        interval: str = "1d",
    ) -> pd.DataFrame | None:
        """Download data from yfinance and normalise columns.

        Returns a DataFrame with columns:
            date, open, high, low, close, adj_close, volume
        """
        try:
            df = yf.download(
                ticker,
                start=start.isoformat(),
                end=(end + dt.timedelta(days=1)).isoformat(),  # yfinance end is exclusive
                interval=interval,
                auto_adjust=True,
                progress=False,
                threads=False,
            )
            if df.empty:
                return None

            # Normalise multi-level columns that yfinance may return
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df = df.reset_index()

            # Rename columns to match our schema
            col_map = {
                "Date": "date",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Adj Close": "adj_close",
                "Volume": "volume",
            }
            df = df.rename(columns=col_map)

            # When auto_adjust=True, Adj Close == Close
            if "adj_close" not in df.columns:
                df["adj_close"] = df["close"]

            # Ensure correct dtypes
            df = df.dropna(
                subset=["open", "high", "low", "close", "volume"]
            )

            return df[["date", "open", "high", "low", "close", "adj_close", "volume"]]

        except Exception as exc:
            logger.warning("yfinance download failed for %s (%s->%s): %s", ticker, start, end, exc)
            return None
