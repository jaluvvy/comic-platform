/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'bizweb.dktcdn.net',
      },
      {
        protocol: 'https',
        hostname: '**.nxbkimdong.com.vn',
      },
    ],
  },
  // Production optimizations
  compress: true,
  poweredByHeader: false,
  generateBuildId: async () => {
    return 'build-' + Date.now();
  },
  // Server-side rendering for dynamic content
  experimental: {
    serverActions: {
      bodySizeLimit: '2mb',
    },
  },
  // Output standalone for Docker/Vercel
  output: 'standalone',
}

module.exports = nextConfig
