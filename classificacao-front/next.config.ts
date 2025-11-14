// next.config.ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/proxy/:path*',
        destination: 'http://classificacao-pesquisadores-api:3001/:path*', 
      },
    ];
  },
  output: 'standalone', // boa prática para Docker
};

export default nextConfig;
