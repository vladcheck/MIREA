import { defineConfig } from "rolldown";

export default defineConfig({
  input: "./src/app/main.tsx",
  output: {
    file: "bundle.js",
  },
});
