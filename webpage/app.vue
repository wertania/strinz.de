<script setup>
import MenuHeader from "~/components/MenuHeader.vue";
import Footer from "~/components/Footer.vue";
import CookieBanner from "~/components/CookieBanner.vue";
</script>

<template>
  <div class="min-h-screen bg-white dark:bg-background-dark">
    <!-- Site Header Menu -->
    <MenuHeader />
    <!-- Page Content -->
    <main class="bg-white dark:bg-background-dark">
      <NuxtPage />
    </main>
    <!-- Site Footer -->
    <Footer />
    <!-- Cookie Banner -->
    <CookieBanner />
  </div>
</template>
