import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable strict mode for better error detection
  reactStrictMode: true,
  // Required for Docker multi-stage build
  output: 'standalone',
};

export default nextConfig;
