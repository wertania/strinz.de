<template>
  <div
    v-if="showBanner"
    id="cookie-banner"
    class="fixed bottom-0 left-0 right-0 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 p-3 shadow-lg z-50"
  >
    <div class="container mx-auto max-w-3xl px-4 sm:px-6">
      <div class="flex flex-col sm:flex-row items-center justify-between gap-3">
        <div class="text-sm text-gray-600 dark:text-gray-300">
          Wir verwenden Cookies, um Ihre Erfahrung auf unserer Website zu
          verbessern. Mit der Nutzung unserer Website stimmen Sie der Verwendung
          von Cookies zu.
        </div>
        <div class="flex gap-3">
          <button
            @click="declineCookies"
            class="px-3 py-1.5 text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md"
          >
            Ablehnen
          </button>
          <button
            @click="acceptCookies"
            class="px-3 py-1.5 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-md"
          >
            Akzeptieren
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useCookieConsent } from "~/composables/useCookieConsent";

const { setCookie, getCookie, initializeGoogleAnalytics } = useCookieConsent();
const showBanner = ref(false);

const acceptCookies = () => {
  setCookie("analytics-consent", "true", 365);
  showBanner.value = false;
  initializeGoogleAnalytics();
};

const declineCookies = () => {
  setCookie("analytics-consent", "false", 365);
  showBanner.value = false;
};

onMounted(() => {
  const consent = getCookie("analytics-consent");
  if (consent === null) {
    showBanner.value = true;
  } else if (consent === "true") {
    showBanner.value = false;
    initializeGoogleAnalytics();
  }
});
</script>
