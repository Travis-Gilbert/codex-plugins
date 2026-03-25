// app/offline/page.tsx
// Branded offline fallback page served by the service worker.

export default function OfflinePage() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-background">
      <div className="text-center space-y-4 max-w-md px-6">
        <div className="text-6xl">&#x1F4E1;</div>
        <h1 className="text-2xl font-bold">You&apos;re offline</h1>
        <p className="text-muted-foreground">
          Check your internet connection and try again. Your pending changes
          will sync automatically when you&apos;re back online.
        </p>
        <button
          onClick={() => window.location.reload()}
          className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition-opacity"
        >
          Retry
        </button>
      </div>
    </div>
  );
}
