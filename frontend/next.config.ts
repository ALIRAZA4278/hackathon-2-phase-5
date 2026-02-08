import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable strict mode for better error detection
  reactStrictMode: true,
  // Required for Docker multi-stage build
  output: 'standalone',
  // Proxy backend API calls through the frontend server
  // so the browser doesn't need to resolve internal K8s service names
  async rewrites() {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://todo-backend:8000";
    return [
      {
        source: "/backend/:path*",
        destination: `${backendUrl}/:path*`,
      },
    ];
  },
};

export default nextConfig;
