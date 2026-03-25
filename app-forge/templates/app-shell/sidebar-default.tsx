// app/(app)/@sidebar/default.tsx
// Default sidebar navigation. Renders when no specific sidebar route matches.

import Link from 'next/link';

const navItems = [
  { label: 'Objects', href: '/objects', icon: '□' },
  { label: 'Graph', href: '/graph', icon: '◇' },
  { label: 'Settings', href: '/settings', icon: '⚙' },
];

export default function SidebarDefault() {
  return (
    <nav className="p-4 space-y-1">
      <div className="px-2 py-4">
        <h2 className="text-lg font-semibold">App Name</h2>
      </div>
      {navItems.map((item) => (
        <Link
          key={item.href}
          href={item.href}
          className="flex items-center gap-3 px-3 py-2 rounded-md text-sm hover:bg-accent transition-colors"
        >
          <span>{item.icon}</span>
          <span>{item.label}</span>
        </Link>
      ))}
    </nav>
  );
}
