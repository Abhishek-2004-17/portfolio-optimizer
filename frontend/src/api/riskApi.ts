import { api } from './client';
import type { RiskDashboardRequest, RiskDashboardResponse } from '@/types/risk';

export const computeDashboard = (data: RiskDashboardRequest): Promise<RiskDashboardResponse> =>
  api.post('/risk/dashboard', data).then((r) => r.data);
