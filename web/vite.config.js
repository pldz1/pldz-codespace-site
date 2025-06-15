import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import path from "path";

export default defineConfig({
  base: "./",
  plugins: [vue()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: "127.0.0.1",
    port: 10060,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:10058",
        changeOrigin: true,
      },
      "/images": {
        target: "http://127.0.0.1:10058",
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "../server/statics",
    emptyOutDir: true,
  },
});
