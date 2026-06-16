import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {remotePatterns: [{ protocol: "https", hostname: "img.sndimg.com" }, { protocol: "https", hostname: "www.tastingtable.com" }]},
};

export default nextConfig;
