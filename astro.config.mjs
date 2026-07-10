// @ts-check
import { defineConfig } from "astro/config";

// Static portfolio site. No framework integrations — plain HTML/CSS/JS output.
export default defineConfig({
  site: "https://aadithva.com",
  output: "static",
  build: {
    format: "directory",
  },
});
