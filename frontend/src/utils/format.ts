export function formatCurrency(value: number | undefined | null): string {
  if (value == null) return '--';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatPercent(value: number | undefined | null, decimals = 1): string {
  if (value == null) return '--';
  return `${(value * 100).toFixed(decimals)}%`;
}

export function formatNumber(value: number | undefined | null, decimals = 2): string {
  if (value == null) return '--';
  return value.toFixed(decimals);
}
