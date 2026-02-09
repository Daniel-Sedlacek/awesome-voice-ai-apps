<script setup>
defineProps({
  item: {
    type: Object,
    required: true,
  },
  language: {
    type: String,
    default: 'en-US',
  },
})

function getLocalizedName(item, language) {
  if (language === 'de-DE' && item.name_de) return item.name_de
  if (language === 'cs-CZ' && item.name_cs) return item.name_cs
  return item.name
}

function getLocalizedDescription(item, language) {
  if (language === 'de-DE' && item.description_de) return item.description_de
  if (language === 'cs-CZ' && item.description_cs) return item.description_cs
  return item.description
}
</script>

<template>
  <div class="bg-white rounded-2xl shadow-md overflow-hidden transition-all hover:shadow-xl hover:-translate-y-1">
    <img
      :src="item.image_url"
      :alt="getLocalizedName(item, language)"
      class="w-full h-40 object-cover"
    />
    <div class="p-4">
      <div class="flex justify-between items-start mb-2">
        <h3 class="font-bold text-gray-900 text-lg leading-tight">
          {{ getLocalizedName(item, language) }}
        </h3>
        <span class="text-mcdonalds-red font-bold text-lg ml-2 whitespace-nowrap">
          ${{ item.price.toFixed(2) }}
        </span>
      </div>
      <p class="text-gray-600 text-sm mb-3 line-clamp-2">
        {{ getLocalizedDescription(item, language) }}
      </p>
      <div class="flex flex-wrap gap-1">
        <span
          v-for="tag in item.tags"
          :key="tag"
          class="px-2 py-0.5 bg-mcdonalds-yellow/20 text-mcdonalds-red text-xs rounded-full font-medium"
        >
          {{ tag }}
        </span>
      </div>
    </div>
  </div>
</template>
