// vite.config.js

import path from "node:path";

import { defineConfig } from "vite";

export default defineConfig({
  root: __dirname,
  base: "/assets/",
  build: {
    outDir: path.join(__dirname, "./assets_compiled/"),
    manifest: "manifest.json",
    assetsDir: "bundled",
    rollupOptions: {
        input: [
          "static/ts/dragndrop.ts"
        ],
    },
    emptyOutDir: true,
    copyPublicDir: false,
  },
});