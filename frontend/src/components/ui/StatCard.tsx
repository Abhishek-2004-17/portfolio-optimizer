import type { ReactNode } from 'react';

interface Props {
  label: string;
  value: string;
  icon?: ReactNode;
  trend?: 'up' | 'down';
}

export function StatCard({ label, value, icon, trend }: Props) {
  const trendColor = trend === 'up' ? 'text-bull' : trend === 'down' ? 'text-bear' : '';

  return (
    <div className="rounded-xl bg-panel p-4 flex flex-col gap-1">
      <div className="flex items-center gap-2 text-muted text-sm">
        {icon}
        <span>{label}</span>
      </div>
      <span className={`text-xl font-semibold ${trendColor}`}>{value}</span>
    </div>
  );
}
