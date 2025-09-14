<script setup lang="ts">
const route = useRoute();
const slug = Array.isArray(route.params.slug)
  ? route.params.slug.join("/")
  : route.params.slug || "";

const { data: page } = await useAsyncData(`history-${slug}`, () =>
  queryCollection("history").path(`/${slug}`).first()
);

useSeoMeta({
  title: page.value?.title,
  description: page.value?.description,
});
</script>

<template>
  <div class="container mx-auto px-4 py-12">
    <ContentRenderer v-if="page" :value="page" />
    <div v-else>Page not found</div>
  </div>
</template>

<style scoped>
/* Base content styling */
:deep(.content) {
  @apply max-w-4xl mx-auto;
}

/* Typography */
:deep(h1) {
  @apply text-5xl font-bold text-gray-900 mb-8 mt-12 leading-tight tracking-tight;
  background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

:deep(h2) {
  @apply text-4xl font-bold text-gray-800 mb-6 mt-10 leading-tight tracking-tight;
  position: relative;
}

:deep(h2::after) {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 0;
  width: 60px;
  height: 3px;
  background: linear-gradient(90deg, #3b82f6, #1d4ed8);
  border-radius: 2px;
}

:deep(h3) {
  @apply text-3xl font-semibold text-gray-800 mb-5 mt-8 leading-tight;
}

:deep(h4) {
  @apply text-2xl font-semibold text-gray-700 mb-4 mt-6 leading-tight;
}

:deep(h5) {
  @apply text-xl font-medium text-gray-700 mb-3 mt-5 leading-tight;
}

:deep(h6) {
  @apply text-lg font-medium text-gray-600 mb-3 mt-4 leading-tight;
}

/* Paragraphs and text */
:deep(p) {
  @apply text-gray-700 mb-6 leading-relaxed text-lg font-light;
  line-height: 1.8;
}

:deep(p:first-of-type) {
  @apply text-xl leading-relaxed;
  font-weight: 300;
}

:deep(strong) {
  @apply font-semibold text-gray-900;
}

:deep(em) {
  @apply italic text-gray-800 font-medium;
}

:deep(small) {
  @apply text-base text-gray-600;
}

/* Links */
:deep(a) {
  @apply text-blue-600 hover:text-blue-700 no-underline relative transition-all duration-300;
  background: linear-gradient(to right, #3b82f6, #1d4ed8);
  background-size: 0% 2px;
  background-position: 0% 100%;
  background-repeat: no-repeat;
}

:deep(a:hover) {
  background-size: 100% 2px;
  transform: translateY(-1px);
}

:deep(a:visited) {
  @apply text-purple-600;
}

/* Lists */
:deep(ul) {
  @apply mb-6 pl-0 space-y-3;
}

:deep(ol) {
  @apply mb-6 pl-0 space-y-3;
}

:deep(li) {
  @apply text-gray-700 leading-relaxed text-lg font-light relative pl-8;
  line-height: 1.7;
}

:deep(ul li) {
  @apply list-none;
}

:deep(ul li::before) {
  content: '•';
  @apply absolute left-0 top-0 text-blue-500 font-bold text-xl;
}

:deep(ol) {
  counter-reset: list-counter;
}

:deep(ol li) {
  @apply list-none;
  counter-increment: list-counter;
}

:deep(ol li::before) {
  content: counter(list-counter) '.';
  @apply absolute left-0 top-0 text-blue-600 font-semibold;
}

/* Nested lists */
:deep(ul ul),
:deep(ol ol),
:deep(ul ol),
:deep(ol ul) {
  @apply mt-3 mb-0 ml-4;
}

:deep(ul ul li::before) {
  content: '◦';
  @apply text-blue-400;
}

:deep(ul ul ul li::before) {
  content: '▪';
  @apply text-blue-300;
}

/* Blockquotes */
:deep(blockquote) {
  @apply border-l-4 border-blue-500 pl-6 py-6 mb-8 italic text-gray-700 bg-gradient-to-r from-blue-50 to-blue-100 rounded-r-lg relative shadow-sm;
  font-size: 1.125rem;
  line-height: 1.8;
}

:deep(blockquote::before) {
  content: '"';
  @apply absolute -top-2 -left-1 text-6xl text-blue-300 font-serif leading-none;
}

:deep(blockquote p) {
  @apply mb-3 last:mb-0 font-medium;
}

/* Code */
:deep(code) {
  @apply bg-gray-100 text-gray-800 px-3 py-1 rounded-md text-sm font-mono border border-gray-200;
  font-weight: 500;
}

:deep(pre) {
  @apply bg-gradient-to-br from-gray-900 to-gray-800 text-gray-100 p-6 rounded-xl mb-8 overflow-x-auto shadow-lg border border-gray-700;
  font-size: 0.875rem;
  line-height: 1.6;
}

:deep(pre code) {
  @apply bg-transparent text-gray-100 px-0 py-0 border-0;
}

/* Tables */
:deep(table) {
  @apply w-full border-collapse mb-8 rounded-xl overflow-hidden shadow-lg bg-white;
  border: none;
}

:deep(th) {
  @apply bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4 text-left font-semibold text-white;
  border: none;
  font-size: 0.875rem;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

:deep(td) {
  @apply px-6 py-4 text-gray-700 border-b border-gray-100;
  font-size: 0.95rem;
  line-height: 1.6;
}

:deep(tbody tr) {
  @apply transition-all duration-200;
}

:deep(tbody tr:nth-child(even)) {
  @apply bg-gray-50;
}

:deep(tbody tr:hover) {
  @apply bg-blue-50 transform scale-[1.01] shadow-md;
}

:deep(tbody tr:last-child td) {
  border-bottom: none;
}

/* Horizontal rule */
:deep(hr) {
  @apply border-0 my-12 relative;
  height: 1px;
  background: linear-gradient(to right, transparent, #d1d5db, transparent);
}

:deep(hr::after) {
  content: '❋';
  @apply absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white px-4 text-gray-400;
}

/* Images */
:deep(img) {
  @apply max-w-full h-auto rounded-xl shadow-xl mb-8 transition-transform duration-300 hover:scale-105;
}

:deep(figure) {
  @apply mb-10 text-center;
}

:deep(figcaption) {
  @apply text-sm text-gray-600 mt-4 italic font-medium bg-gray-50 px-4 py-2 rounded-lg inline-block;
}

/* Definition lists */
:deep(dl) {
  @apply mb-8 bg-gray-50 p-6 rounded-lg;
}

:deep(dt) {
  @apply font-bold text-gray-900 mb-2 text-lg;
}

:deep(dd) {
  @apply text-gray-700 mb-4 ml-6 pl-4 border-l-2 border-blue-200 leading-relaxed;
}

/* Abbreviations */
:deep(abbr) {
  @apply border-b-2 border-dotted border-blue-400 cursor-help transition-colors duration-200 hover:border-blue-600;
}

/* Mark/highlight */
:deep(mark) {
  @apply bg-yellow-300 px-2 py-1 rounded-md font-medium;
  background: linear-gradient(120deg, #fef08a 0%, #fde047 100%);
}

/* Subscript and superscript */
:deep(sub),
:deep(sup) {
  @apply text-xs font-medium;
}

/* Address */
:deep(address) {
  @apply not-italic text-gray-700 mb-6 bg-gray-50 p-4 rounded-lg border-l-4 border-gray-300;
}

/* Details and summary */
:deep(details) {
  @apply mb-8 border border-gray-200 rounded-xl overflow-hidden shadow-sm bg-white;
}

:deep(summary) {
  @apply cursor-pointer bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 font-semibold text-gray-800 hover:from-blue-50 hover:to-blue-100 transition-all duration-300;
  position: relative;
}

:deep(summary::after) {
  content: '+';
  @apply absolute right-6 top-1/2 transform -translate-y-1/2 text-xl font-bold text-gray-600 transition-transform duration-300;
}

:deep(details[open] summary::after) {
  content: '−';
  transform: translateY(-50%) rotate(180deg);
}

:deep(details[open] summary) {
  @apply border-b border-gray-200;
}

:deep(details > *:not(summary)) {
  @apply px-6 py-4;
}

/* Smooth scrolling and reading experience */
:deep(*) {
  scroll-behavior: smooth;
}

/* Selection styling */
:deep(::selection) {
  @apply bg-blue-200 text-blue-900;
}

/* Focus states for accessibility */
:deep(*:focus) {
  @apply outline-none ring-2 ring-blue-500 ring-opacity-50 rounded;
}
</style>