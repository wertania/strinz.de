<template>
  <div class="content-page">
    <component
      v-for="(block, i) in content"
      :key="i"
      :is="componentMap[block.type]"
      v-bind="block.props"
    />
  </div>
</template>

<script setup>
import { useComponentMap } from "~/composables/useComponentMap";

const props = defineProps({
  content: {
    type: Array,
    required: true,
  },
});

const { componentMap } = useComponentMap();
</script>
