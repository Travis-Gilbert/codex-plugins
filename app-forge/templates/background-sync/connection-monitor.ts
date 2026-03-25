// workers/connection-monitor.ts
// Web Worker that polls the backend for new data without blocking the UI thread.

interface PollConfig {
  apiUrl: string;
  token: string;
  pollInterval: number;
  endpoints: string[];
}

let interval: ReturnType<typeof setInterval>;

self.onmessage = (event: MessageEvent) => {
  const { type, config } = event.data;

  if (type === 'START') {
    startPolling(config as PollConfig);
  }

  if (type === 'STOP') {
    clearInterval(interval);
  }

  if (type === 'POLL_NOW') {
    poll(config as PollConfig);
  }
};

function startPolling(config: PollConfig) {
  clearInterval(interval);
  poll(config);
  interval = setInterval(() => poll(config), config.pollInterval);
}

async function poll(config: PollConfig) {
  for (const endpoint of config.endpoints) {
    try {
      const res = await fetch(`${config.apiUrl}${endpoint}`, {
        headers: { Authorization: `Bearer ${config.token}` },
      });
      if (res.ok) {
        const data = await res.json();
        self.postMessage({ type: 'POLL_RESULT', endpoint, data });
      }
    } catch {
      self.postMessage({ type: 'POLL_ERROR', endpoint });
    }
  }
}
