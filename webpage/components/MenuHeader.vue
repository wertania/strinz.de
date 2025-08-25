<script setup>
// Import the menu configuration from the content directory
import menuConfig from "~/content/_menu.json";
import { ref, onMounted, onUnmounted } from "vue";

// State for mobile menu toggle
const menuOpen = ref(false);

// State for dark mode
const isDarkMode = ref(false);

// State for dropdown menu
const activeDropdown = ref(null);

// Function to toggle the mobile menu
function toggleMenu() {
  menuOpen.value = !menuOpen.value;
}

// Function to toggle dropdown
function toggleDropdown(index) {
  activeDropdown.value = activeDropdown.value === index ? null : index;
}

// Function to close dropdown when clicking outside
function handleClickOutside(event) {
  if (!event.target.closest(".dropdown-menu")) {
    activeDropdown.value = null;
  }
}

// Function to toggle dark mode
function toggleDarkMode() {
  console.log("toggleDarkMode");
  if (typeof document !== "undefined") {
    document.body.classList.toggle("dark");
    isDarkMode.value = document.body.classList.contains("dark");
    localStorage.setItem("darkMode", isDarkMode.value);
  }
}

// Initialize dark mode based on user preference
onMounted(() => {
  if (typeof window !== "undefined") {
    if (
      localStorage.getItem("darkMode") === "true" ||
      (!localStorage.getItem("darkMode") &&
        window.matchMedia("(prefers-color-scheme: dark)").matches)
    ) {
      document.body.classList.add("dark");
      isDarkMode.value = true;
    } else {
      document.body.classList.remove("dark");
      isDarkMode.value = false;
    }
  }
  document.addEventListener("click", handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener("click", handleClickOutside);
});
</script>

<template>
  <!-- Header Navigation Bar -->
  <nav
    class="flex flex-col sm:flex-row w-full justify-between items-center px-4 sm:px-6 py-1 bg-background dark:bg-background-dark shadow sm:shadow-none"
  >
    <!-- Logo and Text Section -->
    <div
      class="w-full sm:w-auto self-start sm:self-center flex flex-row sm:flex-none flex-no-wrap justify-between items-center"
    >
      <a
        :href="menuConfig.logoUrl || '/'"
        class="no-underline hover:text-highlight dark:hover:text-highlight-dark hover:no-underline flex flex-row items-center space-x-2"
      >
        <img
          v-if="menuConfig.logoPath"
          :src="menuConfig.logoPath"
          :alt="menuConfig.logoAlt"
          class="h-16 rounded-xl py-1"
        />
        <span
          v-if="menuConfig.logoText"
          class="text-primary dark:text-dark-primary font-bold text-2xl"
          >{{ menuConfig.logoText }}</span
        >
      </a>
      <!-- Hamburger Button for Mobile -->
      <button
        id="menuBtn"
        class="block sm:hidden w-8 h-8 relative focus:outline-none"
        type="button"
        @click="toggleMenu"
        :aria-label="menuOpen ? 'Hide Menu' : 'Show Menu'"
      >
        <!-- Hamburger icon lines -->
        <span
          :class="[
            'absolute w-6 h-0.5 bg-content dark:bg-content-dark rounded transform transition-all duration-300 left-1 top-2',
            menuOpen ? 'rotate-45 translate-y-[7px]' : '',
          ]"
        ></span>
        <span
          :class="[
            'absolute w-6 h-0.5 bg-content dark:bg-content-dark rounded transform transition-all duration-300 left-1 top-4',
            menuOpen ? 'opacity-0' : '',
          ]"
        ></span>
        <span
          :class="[
            'absolute w-6 h-0.5 bg-content dark:bg-content-dark rounded transform transition-all duration-300 left-1 bottom-2',
            menuOpen ? '-rotate-45 -translate-y-[7px]' : '',
          ]"
        ></span>
      </button>
    </div>
    <!-- Menu Items Section -->
    <div
      id="menu"
      :class="[
        'w-full sm:w-auto self-end sm:self-center sm:flex flex-col sm:flex-row items-center h-full py-4 sm:py-0',
        menuOpen ? '' : 'hidden',
        'sm:block',
      ]"
    >
      <div
        class="flex flex-col sm:flex-row space-y-6 sm:space-y-0 sm:space-x-8 items-center w-full sm:w-auto"
      >
        <!-- Render menu items -->
        <template v-for="(item, idx) in menuConfig.menuItems" :key="idx">
          <!-- Dropdown menu item -->
          <div
            v-if="item.subItems"
            class="relative dropdown-menu w-full sm:w-auto"
          >
            <button
              @click="toggleDropdown(idx)"
              class="text-secondary dark:text-dark-secondary font-bold hover:text-primary dark:hover:text-dark-primary text-lg w-full sm:w-auto text-center flex items-center justify-center sm:justify-start"
            >
              {{ item.text }}
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-4 w-4 ml-1"
                :class="{ 'transform rotate-180': activeDropdown === idx }"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </button>
            <!-- Dropdown content -->
            <div
              v-show="activeDropdown === idx"
              class="sm:absolute sm:left-0 sm:mt-2 sm:w-48 sm:rounded-md sm:shadow-lg bg-white dark:bg-background-dark sm:ring-1 sm:ring-black sm:ring-opacity-5 sm:z-50 w-full"
            >
              <div class="py-1">
                <a
                  v-for="(subItem, subIdx) in item.subItems"
                  :key="subIdx"
                  :href="subItem.url"
                  class="block px-4 py-2 text-base text-secondary dark:text-dark-secondary hover:bg-gray-100 dark:hover:bg-gray-700 text-center sm:text-left"
                >
                  {{ subItem.text }}
                </a>
              </div>
            </div>
          </div>
          <!-- Regular menu item -->
          <a
            v-else
            class="text-secondary dark:text-dark-secondary font-bold hover:text-primary dark:hover:text-dark-primary text-lg w-full sm:w-auto text-center"
            :href="item.url"
          >
            {{ item.text }}
          </a>
        </template>
        <!-- Highlight Button -->
        <a
          v-if="menuConfig.highlight"
          :href="menuConfig.highlight.url"
          class="ml-4 px-4 py-2 rounded-full bg-gradient-to-br from-pink-500 to-blue-500 text-white font-medium hover:opacity-90 transition-opacity relative"
          style="background-size: 200% 200%; background-position: 25% 75%"
        >
          <span
            class="absolute inset-0 rounded-full bg-gradient-to-br from-pink-500 to-blue-500 -z-10 blur-[2px]"
          ></span>
          {{ menuConfig.highlight.text }}
        </a>
        <!-- Dark Mode Toggle Button -->
        <button
          id="darkModeToggle"
          class="w-8 h-8 flex items-center justify-center text-content dark:text-content-dark hover:text-primary dark:hover:text-dark-primary"
          @click="toggleDarkMode"
          aria-label="Toggle Dark Mode"
        >
          <!-- Moon icon for dark mode -->
          <svg
            v-if="isDarkMode"
            xmlns="http://www.w3.org/2000/svg"
            class="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
            />
          </svg>
          <!-- Sun icon for light mode -->
          <svg
            v-else
            xmlns="http://www.w3.org/2000/svg"
            class="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
            />
          </svg>
        </button>
      </div>
    </div>
  </nav>
</template>
