<script setup>
defineProps({
  languages: {
    type: Array,
    required: true,
  },
  modelValue: {
    type: String,
    required: true,
  },
})

defineEmits(['update:modelValue'])
</script>

<template>
  <div class="flex gap-2">
    <button
      v-for="lang in languages"
      :key="lang.code"
      @click="$emit('update:modelValue', lang.code)"
      class="px-4 py-2 rounded-full text-sm font-semibold transition-all"
      :class="
        modelValue === lang.code
          ? 'bg-mcdonalds-yellow text-mcdonalds-red shadow-md scale-105'
          : 'bg-white/10 text-white hover:bg-white/20'
      "
    >
      {{ lang.flag }} {{ lang.label }}
    </button>
  </div>
</template>
