// app/(app)/@main/default.tsx
// Default main panel. Renders when no specific main route matches.

export default function MainDefault() {
  return (
    <div className="flex items-center justify-center h-full text-muted-foreground">
      <div className="text-center space-y-2">
        <p className="text-lg">Welcome</p>
        <p className="text-sm">Select an item from the sidebar to get started.</p>
      </div>
    </div>
  );
}
