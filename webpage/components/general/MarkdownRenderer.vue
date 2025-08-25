<template>
  <div v-html="content" class="markdown-content"></div>
</template>

<script setup lang="ts">
import MarkdownIt, {
  type Options as MarkdownItOptions,
  type PluginSimple,
} from "markdown-it";
import { computed, shallowRef } from "vue";

const props = defineProps<{
  source: string;
  options?: MarkdownItOptions;
  plugins?: PluginSimple[];
}>();

const md = shallowRef(new MarkdownIt(props.options ?? {}));

// Apply plugins if provided
for (const plugin of props.plugins ?? []) {
  md.value.use(plugin);
}

const content = computed(() => md.value.render(props.source));
</script>

<style>
.markdown-content {
  /* Add your markdown styling here */
  line-height: 1.6;
}

.markdown-content h1 {
  font-size: 2em;
  margin-bottom: 0.5em;
}

.markdown-content h2 {
  font-size: 1.5em;
  margin-bottom: 0.5em;
}

.markdown-content p {
  margin-bottom: 1em;
}

.markdown-content ul,
.markdown-content ol {
  margin-bottom: 1em;
  padding-left: 2em;
}

.markdown-content code {
  background-color: #f3f4f6;
  padding: 0.2em 0.4em;
  border-radius: 3px;
}

.markdown-content pre {
  background-color: #f3f4f6;
  padding: 1em;
  border-radius: 5px;
  overflow-x: auto;
  margin-bottom: 1em;
}

.markdown-content blockquote {
  border-left: 4px solid #e5e7eb;
  padding-left: 1em;
  margin-left: 0;
  color: #6b7280;
}
</style>
