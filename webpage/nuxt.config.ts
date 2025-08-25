// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2024-11-01",
  devtools: { enabled: true },
  nitro: {
    preset: "static",
  },
  modules: [
    "@nuxtjs/sitemap",
    "@nuxt/content",
    "@nuxtjs/tailwindcss",
    "@nuxt/icon",
    "@nuxt/fonts",
    "@nuxt/scripts",
  ],
  tailwindcss: {
    cssPath: ["~/assets/css/tailwind.css", { injectPosition: "first" }],
    config: {
      content: [
        "./components/**/*.{js,vue,ts}",
        "./layouts/**/*.vue",
        "./pages/**/*.vue",
        "./plugins/**/*.{js,ts}",
        "./app.vue",
        "./error.vue",
      ],
    },
    viewer: true,
    exposeConfig: false,
  },
  app: {
    head: {
      script: [
        {
          src: "/n8n/index.umd.cjs",
          type: "text/javascript",
        },
        {
          src: "/animated-background/three.min.js",
          type: "text/javascript",
        },
        {
          src: "/animated-background/vanta.net.min.js",
          type: "text/javascript",
        },
        {
          src: "/animated-background/vanta.dots.min.js",
          type: "text/javascript",
        },
        {
          src: "/animated-background/vanta.birds.min.js",
          type: "text/javascript",
        },
      ],
    },
  },
  site: {
    url: "https://symbiosika.de",
    name: "Symbiosika AI",
  },
  scripts: {
    registry: {
      googleAnalytics: {
        id: "G-BQZP7Z00PV",
      },
    },
  },
});
