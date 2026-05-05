import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Briefcase, ShieldAlert, GitCompare } from 'lucide-react';
import clsx from 'clsx';

const links = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/build', icon: Briefcase, label: 'Build Portfolio' },
  { to: '/risk', icon: ShieldAlert, label: 'Risk Analysis' },
  { to: '/compare', icon: GitCompare, label: 'Compare' },
];

export function Sidebar() {
  return (
    <aside className="w-64 bg-panel border-r border-panel-light flex flex-col shrink-0">
      <div className="p-6 border-b border-panel-light">
        <h1 className="text-lg font-bold text-brand-500">Portfolio Optimizer</h1>
        <p className="text-xs text-muted mt-1">Finance & Risk Analytics</p>
      </div>
      <nav className="flex-1 p-4 space-y-1">
        {links.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm transition-colors',
                isActive
                  ? 'bg-brand-500/10 text-brand-500 font-medium'
                  : 'text-muted hover:text-slate-100 hover:bg-panel-light'
              )
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
