import { api } from './client';

export const searchTickers = (q: string) =>
  api.get<Array<{ symbol: string; name: string; exchange: string | null }>>('/data/search', { params: { q } }).then((r) => r.data);

export const validateTicker = (ticker: string) =>
  api.get<{ valid: boolean }>(`/data/validate/${ticker}`).then((r) => r.data.valid);
