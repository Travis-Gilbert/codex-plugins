// next.config.ts (desktop app — static export for Tauri)
import type { NextConfig } from 'next';

const config: NextConfig = {
  output: 'export',
  images: {
    unoptimized: true, // No image optimization server in Tauri
  },
};

export default config;
