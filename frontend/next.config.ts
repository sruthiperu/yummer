import type {NextConfig} from "next";

const nextConfig: NextConfig = {};

export default nextConfig;

module.exports = {
    images: {
        remotePatterns: [{hostname: 'img.sndimg.com'}, {hostname: '*.sndimg.com'}, {hostname: 'serpapi.com'}]
    },
}