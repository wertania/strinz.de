<template>
  <div class="max-w-4xl mx-auto py-8 px-4">
    <h1 class="text-4xl font-bold mb-4 text-content dark:text-content-dark">
      {{ title }}
    </h1>
    <h2 class="text-2xl font-semibold mb-4 text-content dark:text-content-dark">
      {{ subtitle }}
    </h2>
    <p class="text-lg text-gray-600 dark:text-gray-400">{{ description }}</p>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },
  subtitle: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    required: true,
  },
});
</script>
