<script setup>
import footerConfig from "~/content/_footer.json";
</script>

<template>
  <footer
    class="w-full bg-background dark:bg-background-dark border-t border-gray-200 dark:border-gray-700"
  >
    <div class="max-w-7xl mx-auto px-4 sm:px-6 py-12">
      <!-- Main Footer Content -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
        <!-- Company Info -->
        <div class="text-center md:text-left">
          <h3
            class="text-lg font-semibold text-primary dark:text-dark-primary mb-4"
          >
            {{ footerConfig?.company.name }}
          </h3>
          <p class="text-sm text-content dark:text-content-dark">
            Ihr Partner für innovative Lösungen
          </p>
        </div>

        <!-- Navigation Links -->
        <div class="text-center">
          <h3
            class="text-lg font-semibold text-primary dark:text-dark-primary mb-4"
          >
            Rechtliches
          </h3>
          <div class="flex flex-col space-y-2">
            <template
              v-for="item in footerConfig?.navigation.filter(
                (nav) => nav.title !== 'LinkedIn'
              )"
              :key="item.url"
            >
              <a
                :href="item.url"
                class="text-secondary dark:text-dark-secondary hover:text-primary dark:hover:text-dark-primary text-sm transition-colors duration-200"
              >
                {{ item.title }}
              </a>
            </template>
          </div>
        </div>

        <!-- Social Media -->
        <div class="text-center md:text-right">
          <h3
            class="text-lg font-semibold text-primary dark:text-dark-primary mb-4"
          >
            Folgen Sie uns
          </h3>
          <div class="flex justify-center md:justify-end space-x-4">
            <template
              v-for="item in footerConfig?.navigation.filter(
                (nav) => nav.title === 'LinkedIn'
              )"
              :key="item.url"
            >
              <a
                :href="item.url"
                target="_blank"
                rel="noopener noreferrer"
                class="text-secondary dark:text-dark-secondary hover:text-primary dark:hover:text-dark-primary transition-colors duration-200"
              >
                <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path
                    d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"
                  />
                </svg>
              </a>
            </template>
          </div>
        </div>
      </div>

      <!-- Memberships Section -->
      <div
        v-if="footerConfig?.memberships"
        class="border-t border-gray-200 dark:border-gray-700 pt-8 mb-8"
      >
        <div class="text-center">
          <h3
            class="text-lg font-semibold text-primary dark:text-dark-primary mb-6"
          >
            Mitgliedschaften
          </h3>
          <div class="flex flex-wrap justify-center items-center gap-8">
            <template
              v-for="membership in footerConfig.memberships"
              :key="membership.name"
            >
              <a
                :href="membership.url"
                target="_blank"
                rel="noopener noreferrer"
                class="block transition-transform duration-200 hover:scale-105 hover:opacity-80"
                :title="membership.name"
              >
                <img
                  :src="membership.logo"
                  :alt="membership.name"
                  class="h-12 w-auto max-w-[120px] object-contain filter grayscale hover:grayscale-0 transition-all duration-300 dark:bg-white dark:rounded-md dark:p-2"
                />
              </a>
            </template>
          </div>
        </div>
      </div>

      <!-- Copyright Section -->
      <div
        class="border-t border-gray-200 dark:border-gray-700 pt-6 text-center"
      >
        <p class="text-sm text-content dark:text-content-dark">
          &copy; {{ new Date().getFullYear() }}
          <a
            :href="footerConfig?.company.url"
            target="_blank"
            rel="noopener noreferrer"
            class="text-highlight dark:text-highlight-dark hover:text-highlight-secondary dark:hover:text-highlight-secondary-dark font-medium transition-colors duration-200 ml-1"
          >
            {{ footerConfig?.company.name }}
          </a>
          - Alle Rechte vorbehalten
        </p>
      </div>
    </div>
  </footer>
</template>
