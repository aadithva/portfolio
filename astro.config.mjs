// @ts-check
import { defineConfig } from "astro/config";

// Static portfolio site; isolated text effects load React on demand.
export default defineConfig({
  site: "https://aadithva.com",
  output: "static",
  build: {
    format: "directory",
  },
});
