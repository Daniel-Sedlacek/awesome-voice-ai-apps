<script setup>
import MenuItemCard from './MenuItemCard.vue'

defineProps({
  items: {
    type: Array,
    required: true,
  },
  language: {
    type: String,
    default: 'en-US',
  },
})

const emit = defineEmits(['add-to-basket'])
</script>

<template>
  <div v-if="items.length === 0" class="text-center py-16">
    <p class="text-white/50 text-lg">Speak to find menu items</p>
  </div>
  <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
    <MenuItemCard
      v-for="item in items"
      :key="item.id"
      :item="item"
      :language="language"
      @add-to-basket="emit('add-to-basket', $event)"
    />
  </div>
</template>
