<template>
  <div class="max-w-4xl mx-auto py-6 px-4">
    <div
      class="company-name text-xl font-semibold mb-2 text-content dark:text-content-dark"
    >
      {{ companyName }}
    </div>
    <div class="address-details text-lg text-gray-700 dark:text-gray-300">
      <div class="street">{{ street }}</div>
      <div class="city">{{ postalCode }} {{ city }}</div>
      <div v-if="country" class="country">{{ country }}</div>
      <div v-if="management" class="management mt-4">
        <span class="font-medium">Geschäftsführung:</span> {{ management }}
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  companyName: {
    type: String,
    required: true,
  },
  street: {
    type: String,
    required: true,
  },
  postalCode: {
    type: String,
    required: true,
  },
  city: {
    type: String,
    required: true,
  },
  country: {
    type: String,
    default: "Deutschland",
  },
  management: {
    type: String,
    default: "",
  },
});
</script>
