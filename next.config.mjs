/** @type {import('next').NextConfig} */
const backend = process.env.BACKEND_ORIGIN;

const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    // Local dev: proxy /api/* to the FastAPI backend (uvicorn on :8000).
    // On Vercel: BACKEND_ORIGIN is unset and /api/* is served by Python functions.
    return backend
      ? [{ source: "/api/:path*", destination: `${backend}/api/:path*` }]
      : [];
  },
};

export default nextConfig;
