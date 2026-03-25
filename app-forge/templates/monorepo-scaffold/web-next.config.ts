// apps/web/next.config.ts (web — full SSR, deployed to Vercel)
import type { NextConfig } from 'next';

const config: NextConfig = {
  transpilePackages: ['@app/ui', '@app/api-client', '@app/shared'],
};

export default config;
