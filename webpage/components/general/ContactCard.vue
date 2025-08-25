<template>
  <div class="relative isolate overflow-hidden">
    <div class="mx-auto max-w-7xl px-6 lg:px-8 pb-6">
      <div class="mx-auto max-w-md lg:max-w-2xl">
        <div
          class="bg-background-secondary dark:bg-background-secondary-dark rounded-2xl shadow-xl overflow-hidden text-center"
        >
          <!-- Profile Image - Centered -->
          <div class="flex justify-center pt-8">
            <template v-if="data.photo">
              <img
                class="h-48 w-48 object-cover rounded-full border-4 border-highlight dark:border-highlight-dark"
                :src="data.photo"
                :alt="`${data.firstName} ${data.lastName}`"
              />
            </template>
            <template v-else>
              <div
                class="h-48 w-48 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center"
              >
                <svg
                  class="h-24 w-24 text-gray-400 dark:text-gray-300"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"
                  ></path>
                </svg>
              </div>
            </template>
          </div>

          <!-- Profile Content -->
          <div class="p-8">
            <h2 class="text-2xl font-bold text-content dark:text-content-dark">
              {{ data.firstName }} {{ data.lastName }}
            </h2>
            <p
              v-if="data.function"
              class="mt-1 text-highlight dark:text-content-dark font-medium"
            >
              {{ data.function }}
            </p>

            <p
              v-if="data.slogan"
              class="mt-4 text-lg italic text-content-secondary dark:text-content-dark"
            >
              "{{ data.slogan }}"
            </p>

            <div
              v-if="data.description"
              class="mt-4 text-content-secondary dark:text-content-dark"
            >
              <p>{{ data.description }}</p>
            </div>

            <!-- Social Media Links -->
            <div
              class="mt-6 flex justify-center items-end space-x-6 pt-12 pb-12"
            >
              <a
                v-if="data.email"
                :href="`mailto:${data.email}`"
                class="group flex flex-col items-center text-gray-400 dark:text-content-dark hover:text-highlight dark:hover:text-highlight-dark"
                :title="data.email"
              >
                <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                  <path
                    d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"
                  ></path>
                </svg>
              </a>
              <a
                v-if="data.phone"
                :href="`tel:${data.phone}`"
                class="group flex flex-col items-center text-gray-400 dark:text-content-dark hover:text-highlight dark:hover:text-highlight-dark"
                :title="data.phone"
              >
                <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                  <path
                    d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"
                  ></path>
                </svg>
              </a>
              <a
                v-if="data.linkedin"
                :href="data.linkedin"
                target="_blank"
                rel="noopener noreferrer"
                class="group flex flex-col items-center text-gray-400 dark:text-content-dark hover:text-highlight dark:hover:text-highlight-dark"
              >
                <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                  <path
                    d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"
                  />
                </svg>
              </a>
              <a
                v-if="data.xing"
                :href="data.xing"
                target="_blank"
                rel="noopener noreferrer"
                class="group flex flex-col items-center text-gray-400 dark:text-content-dark hover:text-highlight dark:hover:text-highlight-dark"
              >
                <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                  <path
                    d="M18.188 0c-.517 0-.741.325-.927.66 0 0-7.455 13.224-7.702 13.657.015.024 4.919 9.023 4.919 9.023.17.308.436.66.967.66h3.454c.211 0 .375-.078.463-.22.089-.151.089-.346-.009-.536l-4.879-8.916c-.004-.006-.004-.016 0-.022L22.139.756c.095-.191.097-.387.006-.535C22.056.078 21.894 0 21.686 0h-3.498zM3.648 4.74c-.211 0-.385.074-.473.216-.09.149-.078.339.02.531l2.34 4.05c.004.01.004.016 0 .021L1.86 16.051c-.099.188-.093.381 0 .529.085.142.239.234.45.234h3.461c.518 0 .766-.348.945-.667l3.734-6.609-2.378-4.155c-.172-.315-.434-.659-.962-.659H3.648v.016z"
                  />
                </svg>
              </a>
              <a
                v-if="data.whatsapp"
                :href="`https://wa.me/${data.whatsapp}`"
                target="_blank"
                rel="noopener noreferrer"
                class="group flex flex-col items-center text-gray-400 dark:text-content-dark hover:text-highlight dark:hover:text-highlight-dark"
              >
                <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                  <path
                    d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"
                  />
                </svg>
              </a>
            </div>

            <!-- vCard Download Button -->
            <div class="mt-8">
              <button
                id="download-vcard"
                class="inline-flex items-center px-6 py-3 border-2 border-highlight dark:border-highlight-dark text-base font-medium rounded-md shadow-md text-content-always-light dark:text-content-dark bg-highlight dark:bg-highlight-dark hover:bg-highlight-secondary dark:hover:bg-highlight-secondary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-highlight dark:focus:ring-highlight-dark"
                @click="generateVCard"
              >
                <svg
                  class="mr-2 h-5 w-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                  ></path>
                </svg>
                vCard herunterladen
              </button>
            </div>

            <!-- Meeting Link -->
            <div v-if="data.meetingLink" class="mt-4">
              <a
                :href="data.meetingLink"
                target="_blank"
                rel="noopener noreferrer"
                class="inline-flex items-center px-6 py-3 border-2 border-highlight dark:border-highlight-dark text-base font-medium rounded-md shadow-md text-content-always-light dark:text-content-dark bg-highlight dark:bg-highlight-dark hover:bg-highlight-secondary dark:hover:bg-highlight-secondary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-highlight dark:focus:ring-highlight-dark"
              >
                <svg
                  class="mr-2 h-5 w-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                  ></path>
                </svg>
                Termin vereinbaren
              </a>
            </div>

            <!-- Website Link -->
            <div v-if="data.website" class="mt-4">
              <a
                :href="data.website"
                target="_blank"
                rel="noopener noreferrer"
                class="inline-flex items-center px-6 py-3 border-2 border-highlight dark:border-highlight-dark text-base font-medium rounded-md shadow-md text-content-always-light dark:text-content-dark bg-highlight dark:bg-highlight-dark hover:bg-highlight-secondary dark:hover:bg-highlight-secondary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-highlight dark:focus:ring-highlight-dark"
              >
                <svg
                  class="mr-2 h-5 w-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  ></path>
                </svg>
                Website besuchen
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "ContactCard",
  props: {
    data: {
      type: Object,
      required: true,
      default: () => ({
        firstName: "",
        lastName: "",
        function: "",
        slogan: "",
        description: "",
        photo: "",
        email: "",
        phone: "",
        linkedin: "",
        xing: "",
        whatsapp: "",
        meetingLink: "",
        website: "",
      }),
    },
  },
  methods: {
    generateVCard() {
      const vCardData = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        `FN:${this.data.firstName} ${this.data.lastName}`,
        `N:${this.data.lastName};${this.data.firstName};;;`,
        this.data.function ? `TITLE:${this.data.function}` : "",
        this.data.email ? `EMAIL;TYPE=INTERNET:${this.data.email}` : "",
        this.data.phone ? `TEL;TYPE=CELL:${this.data.phone}` : "",
        this.data.linkedin ? `URL;TYPE=LinkedIn:${this.data.linkedin}` : "",
        this.data.xing ? `URL;TYPE=XING:${this.data.xing}` : "",
        this.data.website ? `URL;TYPE=WORK:${this.data.website}` : "",
        "ORG:Symbiosika GmbH",
        "END:VCARD",
      ]
        .filter((line) => line !== "")
        .join("\n");

      const blob = new Blob([vCardData], { type: "text/vcard" });
      const url = URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = url;
      link.download = `${this.data.firstName}_${this.data.lastName}.vcf`;
      document.body.appendChild(link);
      link.click();

      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    },
  },
};
</script>
