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
  activeClass: {
    type: String,
    default: 'bg-mcdonalds-yellow text-mcdonalds-red shadow-md scale-105',
  },
  inactiveClass: {
    type: String,
    default: 'bg-white/10 text-white hover:bg-white/20',
  },
})

defineEmits(['update:modelValue'])
</script>

<template>
  <div class="flex gap-2 flex-wrap justify-center">
    <button
      v-for="lang in languages"
      :key="lang.code"
      @click="$emit('update:modelValue', lang.code)"
      class="px-4 py-2 rounded-full text-sm font-semibold transition-all"
      :class="
        modelValue === lang.code
          ? activeClass
          : inactiveClass
      "
    >
      {{ lang.flag }} {{ lang.label }}
    </button>
  </div>
</template>
