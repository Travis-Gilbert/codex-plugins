// app/(app)/@inspector/default.tsx
// Default inspector panel. Renders when no item is selected.

export default function InspectorDefault() {
  return (
    <div className="flex items-center justify-center h-full p-4 text-muted-foreground">
      <p className="text-sm">Select an item to inspect</p>
    </div>
  );
}
