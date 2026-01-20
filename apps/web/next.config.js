/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  
  // Security headers for iframe content
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com",
              "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.tailwindcss.com",
              "font-src 'self' https://fonts.gstatic.com",
              "img-src 'self' data: https:",
              "frame-src 'self' blob:",
            ].join('; '),
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
