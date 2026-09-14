// @ts-check
import { defineConfig } from "astro/config";

// Static portfolio site; isolated text effects load React on demand.
export default defineConfig({
  site: "https://aadithva-portfolio.vercel.app",
  output: "static",
  vite: {
    esbuild: { jsx: "automatic" },
    optimizeDeps: { exclude: ["@designcodeio/threeui"] },
  },
  build: {
    format: "directory",
  },
});
