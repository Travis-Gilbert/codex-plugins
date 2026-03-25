// app/(auth)/layout.tsx
// Auth layout WITHOUT the app shell. Centered card, no sidebar.

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex items-center justify-center min-h-screen bg-muted/30">
      <div className="w-full max-w-md p-8 bg-background rounded-lg border shadow-sm">
        {children}
      </div>
    </div>
  );
}
