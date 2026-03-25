// app/(app)/layout.tsx
// App shell with parallel route slots for sidebar, main, inspector, and modal.
// This layout persists across all navigation within the (app) route group.

export default function AppShell({
  children,
  sidebar,
  main,
  inspector,
  modal,
}: {
  children: React.ReactNode;
  sidebar: React.ReactNode;
  main: React.ReactNode;
  inspector: React.ReactNode;
  modal: React.ReactNode;
}) {
  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar: persistent navigation */}
      <aside className="w-64 shrink-0 border-r bg-muted/30 overflow-auto">
        {sidebar}
      </aside>

      {/* Main content area with optional inspector */}
      <div className="flex-1 flex min-w-0">
        <main className="flex-1 overflow-auto min-w-0" data-panel="main">
          {main}
        </main>

        {/* Inspector: detail/properties panel */}
        <aside className="w-80 shrink-0 border-l overflow-auto">
          {inspector}
        </aside>
      </div>

      {/* Modal overlay slot */}
      {modal}
    </div>
  );
}
