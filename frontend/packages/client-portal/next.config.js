/** @type {import('next').NextConfig} */
const nextConfig = {
  turbopack: {
    root: '../../',
  },
  transpilePackages: ['@eranos/shared'],
};

module.exports = nextConfig;
