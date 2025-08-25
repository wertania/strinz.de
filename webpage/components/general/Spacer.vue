<template>
  <div :style="{ height: computedSize }" class="w-full" />
</template>

<script setup>
const props = defineProps({
  size: {
    type: [String, Number],
    required: true,
  },
});

const computedSize = computed(() => {
  return typeof props.size === "number" ? `${props.size}px` : props.size;
});
</script>
