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
}

module.exports = nextConfig
