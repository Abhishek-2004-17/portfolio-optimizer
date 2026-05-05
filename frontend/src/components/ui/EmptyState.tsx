interface EmptyStateProps {
  title: string;
  description?: string;
}

export function EmptyState({ title, description }: EmptyStateProps) {
  return (
    <div className="border-2 border-dashed border-panel-light rounded-xl p-12 text-center">
      <h3 className="text-muted text-lg mb-2">{title}</h3>
      {description && <p className="text-muted/60 text-sm">{description}</p>}
    </div>
  );
}
