/** @type {import('next').NextConfig} */
const nextConfig = {
  // Allow images from API
  images: {
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8000',
      },
    ],
  },
}

module.exports = nextConfig
