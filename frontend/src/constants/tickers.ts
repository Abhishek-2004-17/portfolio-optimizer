/**
 * @deprecated This file is kept for backwards compatibility.
 * The app now uses the ticker API for comprehensive ticker search.
 * @see /api/tickerApi.ts
 */

export const COMMON_TICKERS = [
  // Tech Giants
  { symbol: 'AAPL', name: 'Apple Inc.' },
  { symbol: 'MSFT', name: 'Microsoft Corporation' },
  { symbol: 'GOOGL', name: 'Alphabet Inc. (Class A)' },
  { symbol: 'GOOG', name: 'Alphabet Inc. (Class C)' },
  { symbol: 'AMZN', name: 'Amazon.com Inc.' },
  { symbol: 'META', name: 'Meta Platforms Inc.' },
  { symbol: 'NVDA', name: 'NVIDIA Corporation' },
  { symbol: 'TSLA', name: 'Tesla Inc.' },
  { symbol: 'AMD', name: 'Advanced Micro Devices' },
  { symbol: 'INTC', name: 'Intel Corporation' },
  { symbol: 'CRM', name: 'Salesforce Inc.' },
  { symbol: 'ORCL', name: 'Oracle Corporation' },
  { symbol: 'ADBE', name: 'Adobe Inc.' },
  { symbol: 'IBM', name: 'IBM' },
  { symbol: 'CSCO', name: 'Cisco Systems' },

  // Financial Services
  { symbol: 'BRK-B', name: 'Berkshire Hathaway Inc.' },
  { symbol: 'JPM', name: 'JPMorgan Chase & Co.' },
  { symbol: 'V', name: 'Visa Inc.' },
  { symbol: 'MA', name: 'Mastercard Inc.' },
  { symbol: 'BAC', name: 'Bank of America Corp.' },
  { symbol: 'WFC', name: 'Wells Fargo & Co.' },
  { symbol: 'GS', name: 'Goldman Sachs Group' },
  { symbol: 'MS', name: 'Morgan Stanley' },
  { symbol: 'BLK', name: 'BlackRock Inc.' },
  { symbol: 'SCHW', name: 'Charles Schwab Corp.' },
  { symbol: 'AXP', name: 'American Express Co.' },

  // Healthcare
  { symbol: 'JNJ', name: 'Johnson & Johnson' },
  { symbol: 'UNH', name: 'UnitedHealth Group Inc.' },
  { symbol: 'PFE', name: 'Pfizer Inc.' },
  { symbol: 'ABBV', name: 'AbbVie Inc.' },
  { symbol: 'TMO', name: 'Thermo Fisher Scientific' },
  { symbol: 'MRK', name: 'Merck & Co. Inc.' },
  { symbol: 'ABT', name: 'Abbott Laboratories' },
  { symbol: 'DHR', name: 'Danaher Corporation' },
  { symbol: 'BMY', name: 'Bristol-Myers Squibb' },
  { symbol: 'LLY', name: 'Eli Lilly and Co.' },
  { symbol: 'AMGN', name: 'Amgen Inc.' },
  { symbol: 'GILD', name: 'Gilead Sciences' },
  { symbol: 'CVS', name: 'CVS Health Corp.' },
  { symbol: 'MDT', name: 'Medtronic plc' },

  // Consumer Goods
  { symbol: 'PG', name: 'Procter & Gamble Co.' },
  { symbol: 'KO', name: 'Coca-Cola Company' },
  { symbol: 'PEP', name: 'PepsiCo Inc.' },
  { symbol: 'NKE', name: 'Nike Inc.' },
  { symbol: 'MCD', name: "McDonald's Corp." },
  { symbol: 'SBUX', name: 'Starbucks Corporation' },
  { symbol: 'COST', name: 'Costco Wholesale Corp.' },
  { symbol: 'WMT', name: 'Walmart Inc.' },
  { symbol: 'HD', name: 'Home Depot Inc.' },
  { symbol: 'TJX', name: 'TJX Companies Inc.' },
  { symbol: 'LOW', name: "Lowe's Companies" },
  { symbol: 'TGT', name: 'Target Corporation' },

  // Energy
  { symbol: 'XOM', name: 'Exxon Mobil Corp.' },
  { symbol: 'CVX', name: 'Chevron Corporation' },
  { symbol: 'COP', name: 'ConocoPhillips' },
  { symbol: 'SLB', name: 'Schlumberger NV' },
  { symbol: 'EOG', name: 'EOG Resources Inc.' },
  { symbol: 'PXD', name: 'Pioneer Natural Resources' },
  { symbol: 'MPC', name: 'Marathon Petroleum' },
  { symbol: 'PSX', name: 'Phillips 66' },
  { symbol: 'VLO', name: 'Valero Energy' },
  { symbol: 'OXY', name: 'Occidental Petroleum' },

  // Industrials
  { symbol: 'CAT', name: 'Caterpillar Inc.' },
  { symbol: 'HON', name: 'Honeywell International' },
  { symbol: 'UPS', name: 'United Parcel Service' },
  { symbol: 'BA', name: 'Boeing Company' },
  { symbol: 'GE', name: 'General Electric' },
  { symbol: 'MMM', name: '3M Company' },
  { symbol: 'RTX', name: 'Raytheon Technologies' },
  { symbol: 'LMT', name: 'Lockheed Martin Corp.' },
  { symbol: 'NOC', name: 'Northrop Grumman Corp.' },
  { symbol: 'DE', name: 'Deere & Company' },
  { symbol: 'UNP', name: 'Union Pacific Corp.' },
  { symbol: 'EMR', name: 'Emerson Electric Co.' },

  // Communication Services
  { symbol: 'DIS', name: 'Walt Disney Company' },
  { symbol: 'NFLX', name: 'Netflix Inc.' },
  { symbol: 'CMCSA', name: 'Comcast Corporation' },
  { symbol: 'T', name: 'AT&T Inc.' },
  { symbol: 'VZ', name: 'Verizon Communications' },
  { symbol: 'TMUS', name: 'T-Mobile US Inc.' },

  // Utilities
  { symbol: 'NEE', name: 'NextEra Energy Inc.' },
  { symbol: 'DUK', name: 'Duke Energy Corp.' },
  { symbol: 'SO', name: 'Southern Company' },
  { symbol: 'D', name: 'Dominion Energy Inc.' },
  { symbol: 'EXC', name: 'Exelon Corporation' },
  { symbol: 'AEP', name: 'American Electric Power' },

  // Real Estate
  { symbol: 'AMT', name: 'American Tower Corp.' },
  { symbol: 'PLD', name: 'Prologis Inc.' },
  { symbol: 'CCI', name: 'Crown Castle Inc.' },
  { symbol: 'EQIX', name: 'Equinix Inc.' },
  { symbol: 'DLR', name: 'Digital Realty Trust' },
  { symbol: 'O', name: 'Realty Income Corporation' },
  { symbol: 'WELL', name: 'Welltower Inc.' },
  { symbol: 'VICI', name: 'VICI Properties Inc.' },

  // Materials
  { symbol: 'LIN', name: 'Linde plc' },
  { symbol: 'APD', name: 'Air Products and Chemicals' },
  { symbol: 'SHW', name: 'Sherwin-Williams Company' },
  { symbol: 'FCX', name: 'Freeport-McMoRan Inc.' },
  { symbol: 'NEM', name: 'Newmont Corporation' },
  { symbol: 'DOW', name: 'Dow Inc.' },
  { symbol: 'DD', name: 'DuPont de Nemours' },

  // ETFs (Exchange Traded Funds)
  { symbol: 'SPY', name: 'SPDR S&P 500 ETF Trust' },
  { symbol: 'QQQ', name: 'Invesco QQQ Trust' },
  { symbol: 'IWM', name: 'iShares Russell 2000 ETF' },
  { symbol: 'VTI', name: 'Vanguard Total Stock Market ETF' },
  { symbol: 'VOO', name: 'Vanguard S&P 500 ETF' },
  { symbol: 'VTV', name: 'Vanguard Value ETF' },
  { symbol: 'VUG', name: 'Vanguard Growth ETF' },
  { symbol: 'GLD', name: 'SPDR Gold Shares' },
  { symbol: 'TLT', name: 'iShares 20+ Year Treasury Bond' },
  { symbol: 'XLE', name: 'Energy Select Sector SPDR' },
  { symbol: 'XLK', name: 'Technology Select Sector SPDR' },
  { symbol: 'XLF', name: 'Financial Select Sector SPDR' },
  { symbol: 'XLV', name: 'Health Care Select Sector SPDR' },
];

/**
 * @deprecated Use the ticker API instead. Kept for fallback.
 */
export function searchTickers(query: string): typeof COMMON_TICKERS {
  if (!query) return COMMON_TICKERS.slice(0, 50);
  const q = query.toUpperCase();
  return COMMON_TICKERS.filter(
    (t) => t.symbol.includes(q) || t.name.toUpperCase().includes(q)
  ).slice(0, 50);
}
