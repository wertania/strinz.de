<template>
  <div class="relative isolate mt-32 px-6 py-32 sm:mt-56 sm:py-40 lg:px-8">
    <svg
      class="absolute inset-0 -z-10 h-full w-full stroke-gray-200 [mask-image:radial-gradient(100%_100%_at_top_right,white,transparent)]"
      aria-hidden="true"
    >
      <defs>
        <pattern
          id="1d4240dd-898f-445f-932d-e2872fd12de3"
          width="200"
          height="200"
          x="50%"
          y="0"
          patternUnits="userSpaceOnUse"
        >
          <path d="M.5 200V.5H200" fill="none" />
        </pattern>
      </defs>
      <svg x="50%" y="0" class="overflow-visible fill-gray-50">
        <path
          d="M-200 0h201v201h-201Z M600 0h201v201h-201Z M-400 600h201v201h-201Z M200 800h201v201h-201Z"
          stroke-width="0"
        />
      </svg>
      <rect
        width="100%"
        height="100%"
        stroke-width="0"
        fill="url(#1d4240dd-898f-445f-932d-e2872fd12de3)"
      />
    </svg>
    <div class="mx-auto max-w-2xl text-center">
      <h2
        class="text-3xl font-bold tracking-tight text-content dark:text-content-dark sm:text-4xl"
      >
        {{ headline }}
      </h2>
      <p
        class="mx-auto mt-6 max-w-xl text-lg leading-8 text-content-secondary dark:text-content-secondary-dark"
      >
        {{ description }}
      </p>
      <div class="mt-10 flex items-center justify-center gap-x-6">
        <a
          :href="ctaUrl"
          class="rounded-md bg-highlight px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-highlight-dark focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-highlight"
        >
          {{ ctaLabel }}
        </a>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  headline: string;
  description: string;
  ctaLabel: string;
  ctaUrl: string;
}>();
</script>
