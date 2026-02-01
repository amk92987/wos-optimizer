/** @type {import('next').NextConfig} */
const nextConfig = {
  // Static HTML/CSS/JS export for S3 + CloudFront hosting
  output: 'export',

  // Allow images from API
  images: {
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8000',
      },
    ],
    // next/image optimization is not supported with static export
    unoptimized: true,
  },
}

module.exports = nextConfig
