import { defineConfig } from "vite";

export default defineConfig({
  root: ".",
  publicDir: "./assets",
  build: {
    minify: true,
    cssMinify: true,
  }
});
