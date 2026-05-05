export interface Asset {
  id: number;
  ticker: string;
  weight: number | null;
  shares: number | null;
  purchase_price: number | null;
  added_at: string;
}

export interface Portfolio {
  id: number;
  name: string;
  description: string | null;
  base_currency: string;
  initial_capital: number;
  created_at: string;
  updated_at: string;
  assets: Asset[];
}

export interface PortfolioCreate {
  name: string;
  description?: string;
  base_currency?: string;
  initial_capital: number;
}

export interface PortfolioAssetCreate {
  ticker: string;
  weight?: number;
  shares?: number;
  purchase_price?: number;
}
