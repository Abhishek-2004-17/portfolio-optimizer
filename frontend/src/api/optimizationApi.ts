import { api } from './client';
import type { OptimizeRequest, OptimizeResponse, TargetRiskRequest, FrontierResponse } from '@/types/optimization';

export const runOptimization = (data: OptimizeRequest): Promise<OptimizeResponse> =>
  api.post(`/optimization/${data.method || 'max-sharpe'}`, data).then((r) => r.data);

export const getEfficientFrontier = (data: OptimizeRequest): Promise<FrontierResponse> =>
  api.post('/optimization/efficient-frontier', { ...data, n_points: 50 }).then((r) => r.data);

export const runTargetRisk = (data: TargetRiskRequest): Promise<OptimizeResponse> =>
  api.post('/optimization/target-risk', data).then((r) => r.data);

export const getOptimizationHistory = (portfolioId: number) =>
  api.get<OptimizeResponse[]>(`/optimization/portfolio/${portfolioId}/history`).then((r) => r.data);
