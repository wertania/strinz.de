<template>
  <div class="max-w-4xl mx-auto py-6 px-4">
    <h3 class="text-2xl font-semibold mb-4 text-content dark:text-content-dark">
      {{ title }}
    </h3>
    <p class="text-lg text-gray-700 dark:text-gray-300">{{ content }}</p>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },
  content: {
    type: String,
    required: true,
  },
});
</script>
