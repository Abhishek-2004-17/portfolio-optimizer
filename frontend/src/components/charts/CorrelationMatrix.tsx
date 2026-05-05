interface Props {
  tickers: string[];
  matrix: Record<string, Record<string, number>>;
}

function correlationColor(value: number): string {
  if (value >= 0) {
    const alpha = value * 0.8;
    return `rgba(16, 185, 129, ${alpha})`;
  }
  const alpha = Math.abs(value) * 0.8;
  return `rgba(239, 68, 68, ${alpha})`;
}

export function CorrelationMatrix({ tickers, matrix }: Props) {
  const cellSize = tickers.length > 6 ? 'w-12 h-12 text-[10px]' : 'w-14 h-14 text-xs';

  return (
    <div className="rounded-xl bg-panel p-4">
      <h3 className="text-sm font-medium text-muted mb-3">Correlation Matrix</h3>
      <div className="overflow-x-auto">
        <div className="inline-block">
          {/* Header row with ticker labels */}
          <div className="flex">
            <div className={`flex-shrink-0 ${cellSize}`} />
            {tickers.map((t) => (
              <div key={t} className={`flex-shrink-0 ${cellSize} flex items-center justify-center text-[10px] text-muted font-medium truncate px-0.5`}>
                {t}
              </div>
            ))}
          </div>
          {/* Data rows */}
          {tickers.map((rowTicker, i) => (
            <div key={rowTicker} className="flex">
              <div className={`flex-shrink-0 ${cellSize} flex items-center justify-center text-[10px] text-muted font-medium truncate px-0.5`}>
                {rowTicker}
              </div>
              {tickers.map((colTicker, j) => {
                const value = matrix[rowTicker]?.[colTicker] ?? 0;
                return (
                  <div
                    key={`${i}-${j}`}
                    className={`flex-shrink-0 ${cellSize} flex items-center justify-center rounded-sm font-medium transition-colors`}
                    style={{ backgroundColor: correlationColor(value) }}
                    title={`${rowTicker}/${colTicker}: ${value.toFixed(2)}`}
                  >
                    <span className={Math.abs(value) > 0.5 ? 'text-white' : 'text-slate-300'}>
                      {value.toFixed(2)}
                    </span>
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
