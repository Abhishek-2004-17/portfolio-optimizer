import { Activity } from 'lucide-react';

export function Navbar() {
  return (
    <header className="h-14 bg-panel border-b border-panel-light flex items-center justify-between px-6 shrink-0">
      <div />
      <div className="flex items-center gap-2 text-xs text-muted">
        <Activity size={14} className="text-bull" />
        <span>Connected</span>
      </div>
    </header>
  );
}
