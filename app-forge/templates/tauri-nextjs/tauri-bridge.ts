// lib/tauri-bridge.ts
// Safe Tauri invoke wrapper with SSR guard.

/**
 * Check if running inside a Tauri WebView.
 * Returns false during SSR and in regular browsers.
 */
export function isTauri(): boolean {
  return typeof window !== 'undefined' && '__TAURI_INTERNALS__' in window;
}

/**
 * Invoke a Tauri command from the frontend.
 * Dynamically imports the Tauri API to avoid SSR errors.
 *
 * @throws Error if called during SSR
 */
export async function invoke<T>(
  cmd: string,
  args?: Record<string, unknown>
): Promise<T> {
  if (typeof window === 'undefined') {
    throw new Error('Tauri invoke called during SSR');
  }
  const { invoke: tauriInvoke } = await import('@tauri-apps/api/core');
  return tauriInvoke<T>(cmd, args);
}

/**
 * Listen to Tauri events from the frontend.
 * Returns an unlisten function.
 */
export async function listenEvent<T>(
  event: string,
  handler: (payload: T) => void
): Promise<() => void> {
  if (typeof window === 'undefined') {
    return () => {};
  }
  const { listen } = await import('@tauri-apps/api/event');
  const unlisten = await listen<T>(event, (e) => handler(e.payload));
  return unlisten;
}
