import logging
from datetime import datetime, timedelta
from functools import lru_cache

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


class TickerService:
    """Service for fetching and searching available stock tickers from Yahoo Finance."""

    # Comprehensive list of major market indices and their ticker patterns
    MARKET_INDICES = [
        "^GSPC", "^DJI", "^IXIC", "^RUT", "^VIX",  # US
        "^FTSE", "^GDAXI", "^FCHI",  # Europe
        "^N225", "^HSI", "^STI",  # Asia
    ]

    @staticmethod
    def _get_snp500_list() -> list[dict]:
        """Get S&P 500 constituent companies. Returns list of {symbol, name}."""
        try:
            # Wikipedia table of S&P 500 companies
            import pandas as pd

            url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            tables = pd.read_html(url)
            sp500 = tables[0]
            return [
                {"symbol": row["Symbol"].replace(".", "-"), "name": row["Security"]}
                for _, row in sp500.iterrows()
            ]
        except Exception as e:
            logger.warning(f"Failed to fetch S&P 500 list: {e}")
            return []

    @staticmethod
    def _get_nasdaq100_list() -> list[dict]:
        """Get NASDAQ-100 constituent companies."""
        try:
            url = "https://en.wikipedia.org/wiki/NASDAQ-100"
            tables = pd.read_html(url)
            nasdaq100 = tables[4]  # The table with NASDAQ-100 components
            return [
                {"symbol": row["Ticker"].replace(".", "-"), "name": row["Company"]}
                for _, row in nasdaq100.iterrows()
                if pd.notna(row.get("Ticker"))
            ]
        except Exception as e:
            logger.warning(f"Failed to fetch NASDAQ-100 list: {e}")
            return []

    @staticmethod
    def _get_dow_jones_list() -> list[dict]:
        """Get Dow Jones Industrial Average companies."""
        try:
            url = "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average"
            tables = pd.read_html(url)
            dow = tables[1]
            return [
                {"symbol": row["Symbol"].replace(".", "-"), "name": row["Company"]}
                for _, row in dow.iterrows()
            ]
        except Exception as e:
            logger.warning(f"Failed to fetch Dow Jones list: {e}")
            return []

    @staticmethod
    def _get_popular_etfs() -> list[dict]:
        """Get list of popular ETFs."""
        return [
            # Broad Market
            {"symbol": "SPY", "name": "SPDR S&P 500 ETF Trust"},
            {"symbol": "IVV", "name": "iShares Core S&P 500 ETF"},
            {"symbol": "VOO", "name": "Vanguard S&P 500 ETF"},
            {"symbol": "VTI", "name": "Vanguard Total Stock Market ETF"},
            {"symbol": "VT", "name": "Vanguard Total World Stock ETF"},
            {"symbol": "QQQ", "name": "Invesco QQQ Trust"},
            {"symbol": "IWM", "name": "iShares Russell 2000 ETF"},
            {"symbol": "VTV", "name": "Vanguard Value ETF"},
            {"symbol": "VUG", "name": "Vanguard Growth ETF"},
            {"symbol": "VO", "name": "Vanguard Mid-Cap ETF"},
            {"symbol": "VB", "name": "Vanguard Small-Cap ETF"},
            {"symbol": "SCHB", "name": "Schwab U.S. Broad Market ETF"},
            # Sector ETFs
            {"symbol": "XLE", "name": "Energy Select Sector SPDR"},
            {"symbol": "XLF", "name": "Financial Select Sector SPDR"},
            {"symbol": "XLU", "name": "Utilities Select Sector SPDR"},
            {"symbol": "XLI", "name": "Industrial Select Sector SPDR"},
            {"symbol": "GDX", "name": "VanEck Gold Miners ETF"},
            {"symbol": "XLK", "name": "Technology Select Sector SPDR"},
            {"symbol": "XLV", "name": "Health Care Select Sector SPDR"},
            {"symbol": "XLY", "name": "Consumer Discretionary SPDR"},
            {"symbol": "XLP", "name": "Consumer Staples SPDR"},
            {"symbol": "XLB", "name": "Materials Select Sector SPDR"},
            {"symbol": "XLRE", "name": "Real Estate Select Sector SPDR"},
            {"symbol": "VNQ", "name": "Vanguard Real Estate ETF"},
            {"symbol": "VHT", "name": "Vanguard Health Care ETF"},
            {"symbol": "VDE", "name": "Vanguard Energy ETF"},
            {"symbol": "VCR", "name": "Vanguard Consumer Discretionary ETF"},
            {"symbol": "VDC", "name": "Vanguard Consumer Staples ETF"},
            {"symbol": "VIS", "name": "Vanguard Industrial ETF"},
            {"symbol": "VGT", "name": "Vanguard Information Technology ETF"},
            {"symbol": "VAW", "name": "Vanguard Materials ETF"},
            {"symbol": "VPU", "name": "Vanguard Utilities ETF"},
            {"symbol": "IYK", "name": "iShares U.S. Consumer Goods ETF"},
            {"symbol": "IYC", "name": "iShares U.S. Consumer Services ETF"},
            {"symbol": "IYE", "name": "iShares U.S. Energy ETF"},
            {"symbol": "IYF", "name": "iShares U.S. Financials ETF"},
            {"symbol": "IYH", "name": "iShares U.S. Healthcare ETF"},
            {"symbol": "IYJ", "name": "iShares U.S. Industrials ETF"},
            {"symbol": "IYM", "name": "iShares U.S. Basic Materials ETF"},
            {"symbol": "IYW", "name": "iShares U.S. Technology ETF"},
            {"symbol": "IDU", "name": "iShares U.S. Utilities ETF"},
            # International
            {"symbol": "EFA", "name": "iShares MSCI EAFE ETF"},
            {"symbol": "EEM", "name": "iShares MSCI Emerging Markets ETF"},
            {"symbol": "VWO", "name": "Vanguard Emerging Markets Stock ETF"},
            {"symbol": "VGK", "name": "Vanguard European Stock ETF"},
            {"symbol": "VPL", "name": "Vanguard Pacific Stock ETF"},
            {"symbol": "VEA", "name": "Vanguard FTSE Developed Markets ETF"},
            {"symbol": "VXUS", "name": "Vanguard Total International Stock ETF"},
            {"symbol": "FXI", "name": "iShares China Large-Cap ETF"},
            {"symbol": "EWJ", "name": "iShares MSCI Japan ETF"},
            {"symbol": "EWG", "name": "iShares MSCI Germany ETF"},
            {"symbol": "EWU", "name": "iShares MSCI United Kingdom ETF"},
            {"symbol": "EWQ", "name": "iShares MSCI France ETF"},
            {"symbol": "EWY", "name": "iShares MSCI South Korea ETF"},
            {"symbol": "EWA", "name": "iShares MSCI Australia ETF"},
            {"symbol": "EWC", "name": "iShares MSCI Canada ETF"},
            {"symbol": "EWW", "name": "iShares MSCI Mexico ETF"},
            {"symbol": "EWZ", "name": "iShares MSCI Brazil ETF"},
            {"symbol": "INDA", "name": "iShares MSCI India ETF"},
            # Bond/Fixed Income
            {"symbol": "TLT", "name": "iShares 20+ Year Treasury Bond ETF"},
            {"symbol": "IEF", "name": "iShares 7-10 Year Treasury Bond ETF"},
            {"symbol": "SHY", "name": "iShares 1-3 Year Treasury Bond ETF"},
            {"symbol": "GOVT", "name": "iShares U.S. Treasury Bond ETF"},
            {"symbol": "BND", "name": "Vanguard Total Bond Market ETF"},
            {"symbol": "VCIT", "name": "Vanguard Intermediate-Term Corporate Bond ETF"},
            {"symbol": "VCSH", "name": "Vanguard Short-Term Corporate Bond ETF"},
            {"symbol": "LQD", "name": "iShares Investment Grade Corporate Bond ETF"},
            {"symbol": "HYG", "name": "iShares iBoxx High Yield Corporate Bond ETF"},
            {"symbol": "JNK", "name": "SPDR Bloomberg High Yield Bond ETF"},
            {"symbol": "AGG", "name": "iShares Core U.S. Aggregate Bond ETF"},
            {"symbol": "TLT", "name": "iShares 20+ Year Treasury Bond ETF"},
            {"symbol": "TIP", "name": "iShares TIPS Bond ETF"},
            {"symbol": "MUB", "name": "iShares National Muni Bond ETF"},
            {"symbol": "VGIT", "name": "Vanguard Intermediate-Term Treasury Bond ETF"},
            {"symbol": "BIL", "name": "SPDR Bloomberg 1-3 Month T-Bill ETF"},
            {"symbol": "SHV", "name": "iShares Short Treasury Bond ETF"},
            {"symbol": "SPTL", "name": "SPDR Portfolio Long Term Treasury ETF"},
            {"symbol": "SPTS", "name": "SPDR Portfolio Short Term Treasury ETF"},
            # Commodities
            {"symbol": "GLD", "name": "SPDR Gold Shares"},
            {"symbol": "IAU", "name": "iShares Gold Trust"},
            {"symbol": "SLV", "name": "iShares Silver Trust"},
            {"symbol": "USO", "name": "United States Oil Fund"},
            {"symbol": "DBO", "name": "Invesco DB Oil Fund"},
            {"symbol": "UNG", "name": "United States Natural Gas Fund"},
            {"symbol": "DBC", "name": "Invesco DB Commodity Index ETF"},
            {"symbol": "PDBC", "name": "Invesco Optimum Yield Diversified Commodity Strategy ETF"},
            {"symbol": "WEAT", "name": "Teucrium Wheat Fund"},
            {"symbol": "CORN", "name": "Teucrium Corn Fund"},
            {"symbol": "SOYB", "name": "Teucrium Soybean Fund"},
            # Volatility
            {"symbol": "VXX", "name": "iPath Series B S&P 500 VIX Short-Term Futures ETN"},
            {"symbol": "UVXY", "name": "ProShares Ultra VIX Short-Term Futures ETF"},
            {"symbol": "VIXY", "name": "ProShares VIX Short-Term Futures ETF"},
            # Leveraged/Inverse
            {"symbol": "SPXL", "name": "Direxion Daily S&P 500 Bull 3X Shares"},
            {"symbol": "SPXS", "name": "Direxion Daily S&P 500 Bear 3X Shares"},
            {"symbol": "TQQQ", "name": "ProShares UltraPro QQQ"},
            {"symbol": "SQQQ", "name": "ProShares UltraPro Short QQQ"},
            {"symbol": "SOXL", "name": "Direxion Daily Semiconductor Bull 3X Shares"},
            {"symbol": "SOXS", "name": "Direxion Daily Semiconductor Bear 3X Shares"},
            {"symbol": "UDOW", "name": "ProShares UltraPro Dow30"},
            {"symbol": "SDOW", "name": "ProShares UltraPro Short Dow30"},
            # Dividend
            {"symbol": "DIV", "name": "Global X SuperDividend ETF"},
            {"symbol": "SCHD", "name": "Schwab U.S. Dividend Equity ETF"},
            {"symbol": "VIG", "name": "Vanguard Dividend Appreciation ETF"},
            {"symbol": "DVY", "name": "iShares Select Dividend ETF"},
            {"symbol": "HDV", "name": "iShares Core High Dividend ETF"},
            {"symbol": "DGRO", "name": "iShares Core Dividend Growth ETF"},
            {"symbol": "PFF", "name": "iShares Preferred & Income Securities ETF"},
            {"symbol": "VYM", "name": "Vanguard High Dividend Yield ETF"},
            # REITs
            {"symbol": "VNQ", "name": "Vanguard Real Estate ETF"},
            {"symbol": "IYR", "name": "iShares U.S. Real Estate ETF"},
            {"symbol": "O", "name": "Realty Income Corporation"},
            {"symbol": "XLRE", "name": "Real Estate Select Sector SPDR"},
            # Crypto
            {"symbol": "BITO", "name": "ProShares Bitcoin Strategy ETF"},
            {"symbol": "BITO", "name": "ProShares Bitcoin Strategy ETF"},
            {"symbol": "ETHW", "name": "Ethereum Futures Strategy ETF"},
        ]

    @staticmethod
    def _get_popular_stocks() -> list[dict]:
        """Get list of popular individual stocks by sector."""
        return [
            # Technology
            {"symbol": "AAPL", "name": "Apple Inc."},
            {"symbol": "MSFT", "name": "Microsoft Corporation"},
            {"symbol": "GOOGL", "name": "Alphabet Inc. Class A"},
            {"symbol": "GOOG", "name": "Alphabet Inc. Class C"},
            {"symbol": "AMZN", "name": "Amazon.com Inc."},
            {"symbol": "META", "name": "Meta Platforms Inc."},
            {"symbol": "NVDA", "name": "NVIDIA Corporation"},
            {"symbol": "TSLA", "name": "Tesla Inc."},
            {"symbol": "AMD", "name": "Advanced Micro Devices"},
            {"symbol": "INTC", "name": "Intel Corporation"},
            {"symbol": "CRM", "name": "Salesforce Inc."},
            {"symbol": "ORCL", "name": "Oracle Corporation"},
            {"symbol": "ADBE", "name": "Adobe Inc."},
            {"symbol": "IBM", "name": "International Business Machines"},
            {"symbol": "CSCO", "name": "Cisco Systems Inc."},
            {"symbol": "AVGO", "name": "Broadcom Inc."},
            {"symbol": "QCOM", "name": "Qualcomm Incorporated"},
            {"symbol": "TXN", "name": "Texas Instruments Incorporated"},
            {"symbol": "SHOP", "name": "Shopify Inc."},
            {"symbol": "SQ", "name": "Block Inc."},
            {"symbol": "SNOW", "name": "Snowflake Inc."},
            {"symbol": "PLTR", "name": "Palantir Technologies Inc."},
            {"symbol": "UBER", "name": "Uber Technologies Inc."},
            {"symbol": "LYFT", "name": "Lyft Inc."},
            # Financial
            {"symbol": "BRK-B", "name": "Berkshire Hathaway Inc."},
            {"symbol": "JPM", "name": "JPMorgan Chase & Co."},
            {"symbol": "V", "name": "Visa Inc."},
            {"symbol": "MA", "name": "Mastercard Incorporated"},
            {"symbol": "BAC", "name": "Bank of America Corporation"},
            {"symbol": "WFC", "name": "Wells Fargo & Company"},
            {"symbol": "GS", "name": "The Goldman Sachs Group Inc."},
            {"symbol": "MS", "name": "Morgan Stanley"},
            {"symbol": "BLK", "name": "BlackRock Inc."},
            {"symbol": "SCHW", "name": "The Charles Schwab Corporation"},
            {"symbol": "AXP", "name": "American Express Company"},
            {"symbol": "C", "name": "Citigroup Inc."},
            {"symbol": "USB", "name": "U.S. Bancorp"},
            {"symbol": "PNC", "name": "The PNC Financial Services Group"},
            {"symbol": "COF", "name": "Capital One Financial"},
            # Healthcare
            {"symbol": "JNJ", "name": "Johnson & Johnson"},
            {"symbol": "UNH", "name": "UnitedHealth Group Incorporated"},
            {"symbol": "PFE", "name": "Pfizer Inc."},
            {"symbol": "ABBV", "name": "AbbVie Inc."},
            {"symbol": "TMO", "name": "Thermo Fisher Scientific Inc."},
            {"symbol": "MRK", "name": "Merck & Co. Inc."},
            {"symbol": "ABT", "name": "Abbott Laboratories"},
            {"symbol": "DHR", "name": "Danaher Corporation"},
            {"symbol": "BMY", "name": "Bristol-Myers Squibb Company"},
            {"symbol": "LLY", "name": "Eli Lilly and Company"},
            {"symbol": "AMGN", "name": "Amgen Inc."},
            {"symbol": "GILD", "name": "Gilead Sciences Inc."},
            {"symbol": "CVS", "name": "CVS Health Corporation"},
            {"symbol": "MDT", "name": "Medtronic plc"},
            {"symbol": "ISRG", "name": "Intuitive Surgical Inc."},
            {"symbol": "REGN", "name": "Regeneron Pharmaceuticals"},
            {"symbol": "BIIB", "name": "Biogen Inc."},
            {"symbol": "MRNA", "name": "Moderna Inc."},
            {"symbol": "VRTX", "name": "Vertex Pharmaceuticals Incorporated"},
            # Consumer
            {"symbol": "PG", "name": "Procter & Gamble Company"},
            {"symbol": "KO", "name": "The Coca-Cola Company"},
            {"symbol": "PEP", "name": "PepsiCo Inc."},
            {"symbol": "NKE", "name": "Nike Inc."},
            {"symbol": "MCD", "name": "McDonald's Corporation"},
            {"symbol": "SBUX", "name": "Starbucks Corporation"},
            {"symbol": "COST", "name": "Costco Wholesale Corporation"},
            {"symbol": "WMT", "name": "Walmart Inc."},
            {"symbol": "HD", "name": "The Home Depot Inc."},
            {"symbol": "TJX", "name": "The TJX Companies Inc."},
            {"symbol": "LOW", "name": "Lowe's Companies Inc."},
            {"symbol": "TGT", "name": "Target Corporation"},
            {"symbol": "BKNG", "name": "Booking Holdings Inc."},
            {"symbol": "MAR", "name": "Marriott International"},
            {"symbol": "HLT", "name": "Hilton Worldwide Holdings"},
            {"symbol": "YUM", "name": "Yum! Brands"},
            {"symbol": "DRI", "name": "Darden Restaurants"},
            # Energy
            {"symbol": "XOM", "name": "Exxon Mobil Corporation"},
            {"symbol": "CVX", "name": "Chevron Corporation"},
            {"symbol": "COP", "name": "ConocoPhillips"},
            {"symbol": "SLB", "name": "Schlumberger NV"},
            {"symbol": "EOG", "name": "EOG Resources Inc."},
            {"symbol": "PXD", "name": "Pioneer Natural Resources Company"},
            {"symbol": "MPC", "name": "Marathon Petroleum Corporation"},
            {"symbol": "PSX", "name": "Phillips 66"},
            {"symbol": "VLO", "name": "Valero Energy Corporation"},
            {"symbol": "OXY", "name": "Occidental Petroleum"},
            {"symbol": "HAL", "name": "Halliburton Company"},
            {"symbol": "BKR", "name": "Baker Hughes Company"},
            # Industrials
            {"symbol": "CAT", "name": "Caterpillar Inc."},
            {"symbol": "HON", "name": "Honeywell International Inc."},
            {"symbol": "UPS", "name": "United Parcel Service Inc."},
            {"symbol": "BA", "name": "The Boeing Company"},
            {"symbol": "GE", "name": "General Electric Company"},
            {"symbol": "MMM", "name": "3M Company"},
            {"symbol": "RTX", "name": "Raytheon Technologies Corporation"},
            {"symbol": "LMT", "name": "Lockheed Martin Corporation"},
            {"symbol": "NOC", "name": "Northrop Grumman Corporation"},
            {"symbol": "DE", "name": "Deere & Company"},
            {"symbol": "UNP", "name": "Union Pacific Corporation"},
            {"symbol": "EMR", "name": "Emerson Electric Co."},
            {"symbol": "FDX", "name": "FedEx Corporation"},
            {"symbol": "CSX", "name": "CSX Corporation"},
            {"symbol": "NSC", "name": "Norfolk Southern Corporation"},
            {"symbol": "CAT", "name": "Caterpillar Inc."},
            # Communication
            {"symbol": "DIS", "name": "The Walt Disney Company"},
            {"symbol": "NFLX", "name": "Netflix Inc."},
            {"symbol": "CMCSA", "name": "Comcast Corporation"},
            {"symbol": "T", "name": "AT&T Inc."},
            {"symbol": "VZ", "name": "Verizon Communications Inc."},
            {"symbol": "TMUS", "name": "T-Mobile US Inc."},
            {"symbol": "FOX", "name": "FOX Corporation"},
            {"symbol": "FOXA", "name": "FOX Corporation Class A"},
            {"symbol": "PARA", "name": "Paramount Global"},
            # Utilities
            {"symbol": "NEE", "name": "NextEra Energy Inc."},
            {"symbol": "DUK", "name": "Duke Energy Corporation"},
            {"symbol": "SO", "name": "Southern Company"},
            {"symbol": "D", "name": "Dominion Energy Inc."},
            {"symbol": "EXC", "name": "Exelon Corporation"},
            {"symbol": "AEP", "name": "American Electric Power Company"},
            {"symbol": "XEL", "name": "Xcel Energy Inc."},
            {"symbol": "ED", "name": "Consolidated Edison Inc."},
            # Real Estate
            {"symbol": "AMT", "name": "American Tower Corporation"},
            {"symbol": "PLD", "name": "Prologis Inc."},
            {"symbol": "CCI", "name": "Crown Castle Inc."},
            {"symbol": "EQIX", "name": "Equinix Inc."},
            {"symbol": "DLR", "name": "Digital Realty Trust Inc."},
            {"symbol": "WELL", "name": "Welltower Inc."},
            {"symbol": "VICI", "name": "VICI Properties Inc."},
            {"symbol": "SPG", "name": "Simon Property Group"},
            {"symbol": "CBRE", "name": "CBRE Group"},
            # Materials
            {"symbol": "LIN", "name": "Linde plc"},
            {"symbol": "APD", "name": "Air Products and Chemicals Inc."},
            {"symbol": "SHW", "name": "The Sherwin-Williams Company"},
            {"symbol": "FCX", "name": "Freeport-McMoRan Inc."},
            {"symbol": "NEM", "name": "Newmont Corporation"},
            {"symbol": "DOW", "name": "Dow Inc."},
            {"symbol": "DD", "name": "DuPont de Nemours Inc."},
            {"symbol": "PPG", "name": "PPG Industries Inc."},
            {"symbol": "IP", "name": "International Paper Company"},
            # Other notable stocks
            {"symbol": "GME", "name": "GameStop Corporation"},
            {"symbol": "AMC", "name": "AMC Entertainment Holdings"},
            {"symbol": "BB", "name": "BlackBerry Limited"},
            {"symbol": "NOK", "name": "Nokia Corporation"},
            {"symbol": "BBY", "name": "Best Buy Co. Inc."},
            {"symbol": "ROST", "name": "Ross Stores Inc."},
            {"symbol": "DG", "name": "Dollar General Corporation"},
            {"symbol": "DLTR", "name": "Dollar Tree Inc."},
        ]

    @classmethod
    def fetch_all_tickers(cls, force_refresh: bool = False) -> list[dict]:
        """
        Fetch all available tickers from multiple sources.
        Returns list of {symbol, name} dictionaries.
        """
        tickers = []

        # Get all sources
        sp500 = cls._get_snp500_list()
        nasdaq100 = cls._get_nasdaq100_list()
        dow = cls._get_dow_jones_list()
        etfs = cls._get_popular_etfs()
        popular = cls._get_popular_stocks()

        # Combine all
        all_tickers = sp500 + nasdaq100 + dow + etfs + popular

        # Remove duplicates by symbol (keep first occurrence)
        seen = set()
        unique_tickers = []
        for ticker in all_tickers:
            symbol = ticker["symbol"]
            if symbol not in seen:
                seen.add(symbol)
                unique_tickers.append(ticker)

        # Validate tickers exist on Yahoo Finance
        validated = cls._validate_tickers(unique_tickers)

        logger.info(f"Fetched {len(validated)} valid tickers")
        return validated

    @staticmethod
    def _validate_tickers(tickers: list[dict], batch_size: int = 100) -> list[dict]:
        """
        Validate that tickers exist on Yahoo Finance.
        Returns only validated tickers.
        """
        validated = []
        total = len(tickers)

        for i in range(0, total, batch_size):
            batch = tickers[i : i + batch_size]
            symbols = [t["symbol"] for t in batch]

            try:
                # Download just the most recent data to validate
                data = yf.download(
                    symbols,
                    period="1d",
                    progress=False,
                    threads=False,
                )

                # Check which symbols returned data
                if isinstance(data, pd.DataFrame) and "Close" in data:
                    valid_symbols = set(data["Close"].columns)
                else:
                    valid_symbols = set()

                for ticker in batch:
                    if ticker["symbol"] in valid_symbols:
                        validated.append(ticker)

            except Exception as e:
                logger.warning(f"Validation batch {i}-{i+batch_size} failed: {e}")
                # If batch fails, include all tickers anyway
                validated.extend(batch)

        return validated

    @staticmethod
    def search_tickers(query: str, tickers: list[dict] | None = None, limit: int = 50) -> list[dict]:
        """
        Search tickers by symbol or name.
        """
        if tickers is None:
            tickers = TickerService.fetch_all_tickers()

        if not query:
            return tickers[:limit]

        q = query.upper()
        matches = []

        # First, exact symbol match
        for ticker in tickers:
            if ticker["symbol"] == q:
                matches.append(ticker)
                if len(matches) >= limit:
                    return matches

        # Then, prefix symbol match
        for ticker in tickers:
            if ticker["symbol"].startswith(q) and ticker not in matches:
                matches.append(ticker)
                if len(matches) >= limit:
                    return matches

        # Then, symbol contains
        for ticker in tickers:
            if q in ticker["symbol"] and ticker not in matches:
                matches.append(ticker)
                if len(matches) >= limit:
                    return matches

        # Finally, name contains
        for ticker in tickers:
            if q in ticker["name"].upper() and ticker not in matches:
                matches.append(ticker)
                if len(matches) >= limit:
                    return matches

        return matches

    @staticmethod
    def validate_ticker(ticker: str) -> bool:
        """
        Validate a single ticker symbol.
        Returns True if the ticker exists on Yahoo Finance.
        """
        try:
            data = yf.download(ticker, period="1d", progress=False, threads=False)
            return not data.empty
        except Exception:
            return False
