// apps/desktop/next.config.ts (desktop — static export for Tauri)
import type { NextConfig } from 'next';

const config: NextConfig = {
  output: 'export',
  images: { unoptimized: true },
  transpilePackages: ['@app/ui', '@app/api-client', '@app/shared'],
};

export default config;
