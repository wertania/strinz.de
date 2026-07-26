import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";

// A fully pre-rendered, static site: every page is HTML on disk after `build`.
export default defineConfig({
  site: "https://strinz.de",
  output: "static",
  trailingSlash: "always",
  build: { format: "directory", inlineStylesheets: "auto" },
  integrations: [sitemap()],
  compressHTML: true,
  devToolbar: { enabled: false },
});
