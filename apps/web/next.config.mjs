/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  devIndicators: false,
  distDir: process.env.MDI_NEXT_DIST_DIR || ".cache/next",
  experimental: {
    // Next's rewrite proxy clones request bodies before passing them through.
    // Keep that internal stream cap aligned with the existing public per-file
    // upload cap so normal browser uploads are not truncated at Next's 10 MiB
    // default before reaching the streaming API endpoint.
    middlewareClientMaxBodySize: 64 * 1024 * 1024,
  },
  webpack(config) {
    config.ignoreWarnings = [
      ...(config.ignoreWarnings || []),
      {
        message:
          /Critical dependency: the request of a dependency is an expression/u,
        module: /node_modules[\\/]glslify-deps[\\/]sync\.js$/u,
      },
      {
        message:
          /Critical dependency: the request of a dependency is an expression/u,
        module: /node_modules[\\/]glslify[\\/]transform\.js$/u,
      },
    ];
    return config;
  },
  async rewrites() {
    const apiTarget = (
      process.env.MDI_API_PROXY_TARGET ||
      process.env.NEXT_PUBLIC_MDI_API_BASE_URL ||
      "http://127.0.0.1:8000"
    ).replace(/\/$/u, "");
    return [{ source: "/api/:path*", destination: `${apiTarget}/:path*` }];
  },
};

export default nextConfig;
