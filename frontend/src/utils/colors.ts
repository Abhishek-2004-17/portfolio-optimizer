export const CHART_COLORS = [
  '#0ea5e9', '#8b5cf6', '#f59e0b', '#10b981', '#ef4444',
  '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1',
];

export function getColor(index: number): string {
  return CHART_COLORS[index % CHART_COLORS.length];
}

export function getPerformanceColor(value: number): string {
  if (value > 0) return '#10b981';
  if (value < 0) return '#ef4444';
  return '#94a3b8';
}
