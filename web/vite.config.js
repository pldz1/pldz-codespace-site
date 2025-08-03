import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import path from "path";

export default defineConfig({
  base: "/",
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
      // 以 /api和/codespace 开头的请求都走同一套配置
      "^/(api|io)": {
        target: "http://127.0.0.1:10058",
        changeOrigin: true,
        // （可选）如果想在转发时删掉前缀：
        // rewrite: path => path.replace(/^\/(api|io)/, '')
      },
    },
  },
  build: {
    outDir: "../data/templates/statics",
    emptyOutDir: true,
  },
});
