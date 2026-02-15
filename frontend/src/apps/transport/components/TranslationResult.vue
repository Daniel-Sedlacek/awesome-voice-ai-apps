<script setup>
defineProps({
  label: {
    type: String,
    required: true,
  },
  text: {
    type: String,
    required: true,
  },
  locale: {
    type: String,
    default: '',
  },
})
</script>

<template>
  <div class="bg-white/10 rounded-xl p-4">
    <p class="text-transport-light text-sm font-semibold mb-1">{{ label }}</p>
    <p class="text-white text-lg">{{ text }}</p>
    <p v-if="locale" class="text-white/40 text-xs mt-1">{{ locale }}</p>
  </div>
</template>
