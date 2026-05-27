import { defineConfig } from "vite";
import path from "node:path";

export default defineConfig({
  base: ".",
  root: "./src",
  resolve: {
    alias: {
      // oxlint-disable-next-line unicorn/prefer-module
      "@/": path.resolve(__dirname, "src"),
    },
  },
});
