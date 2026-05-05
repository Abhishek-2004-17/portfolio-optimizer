import { api } from './client';
import type { Portfolio, PortfolioCreate, PortfolioAssetCreate, Asset } from '@/types/portfolio';

export const createPortfolio = (data: PortfolioCreate) =>
  api.post<Portfolio>('/portfolios', data).then((r) => r.data);

export const listPortfolios = (skip = 0, limit = 100) =>
  api.get<Portfolio[]>('/portfolios', { params: { skip, limit } }).then((r) => r.data);

export const getPortfolio = (id: number) =>
  api.get<Portfolio>(`/portfolios/${id}`).then((r) => r.data);

export const updatePortfolio = (id: number, data: Partial<PortfolioCreate>) =>
  api.put<Portfolio>(`/portfolios/${id}`, data).then((r) => r.data);

export const deletePortfolio = (id: number) =>
  api.delete(`/portfolios/${id}`);

export const addAsset = (portfolioId: number, data: PortfolioAssetCreate) =>
  api.post<Asset>(`/portfolios/${portfolioId}/assets`, data).then((r) => r.data);

export const removeAsset = (portfolioId: number, assetId: number) =>
  api.delete(`/portfolios/${portfolioId}/assets/${assetId}`);
