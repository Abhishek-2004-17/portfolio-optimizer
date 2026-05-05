interface ErrorPanelProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorPanel({ message, onRetry }: ErrorPanelProps) {
  return (
    <div className="bg-bear/10 border border-bear/30 rounded-xl p-6 text-center">
      <p className="text-bear mb-3">{message}</p>
      {onRetry && (
        <button onClick={onRetry} className="text-sm text-brand-500 hover:underline">
          Retry
        </button>
      )}
    </div>
  );
}
