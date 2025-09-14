import { defineContentConfig, defineCollection, z } from "@nuxt/content";

export default defineContentConfig({
  collections: {
    history: defineCollection({
      source: "history/*.md",
      type: "page",
      // Define custom schema for docs collection
      schema: z.object({
        name: z.string().optional(),
        title: z.string().optional(),
        author: z.string().optional(),
        tags: z.array(z.string()).optional(),
        image: z.string().optional(),
        date: z.date().optional(),
      }),
    }),
  },
});
