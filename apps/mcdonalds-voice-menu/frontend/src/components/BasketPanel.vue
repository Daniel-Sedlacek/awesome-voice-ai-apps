<script setup>
defineProps({
  items: {
    type: Array,
    required: true,
  },
  language: {
    type: String,
    default: 'en-US',
  },
  total: {
    type: Number,
    default: 0,
  },
})

const emit = defineEmits(['remove'])

function getLocalizedName(item, language) {
  if (language === 'de-DE' && item.name_de) return item.name_de
  if (language === 'cs-CZ' && item.name_cs) return item.name_cs
  return item.name
}
</script>

<template>
  <div class="bg-white/10 backdrop-blur-sm rounded-2xl p-4">
    <h2 class="text-mcdonalds-yellow font-bold text-xl mb-4 flex items-center gap-2">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none"
           viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round"
              d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
      </svg>
      My Order
      <span
        v-if="items.length"
        class="bg-mcdonalds-yellow text-mcdonalds-red text-sm rounded-full w-6 h-6 flex items-center justify-center font-bold"
      >
        {{ items.reduce((sum, i) => sum + (i.quantity || 1), 0) }}
      </span>
    </h2>

    <!-- Empty state -->
    <div v-if="items.length === 0" class="text-center py-8">
      <p class="text-white/40 text-sm">
        Say "I'll take the..." or click + to add items
      </p>
    </div>

    <!-- Basket items list -->
    <ul v-else class="space-y-3">
      <li
        v-for="item in items"
        :key="item.id"
        class="flex items-center justify-between bg-white/10 rounded-xl p-3 transition-all hover:bg-white/15"
      >
        <div class="flex items-center gap-3 min-w-0">
          <img
            :src="item.image_url"
            :alt="getLocalizedName(item, language)"
            class="w-10 h-10 rounded-lg object-cover shrink-0"
          />
          <div class="min-w-0">
            <p class="text-white font-medium text-sm truncate">
              <span v-if="item.quantity > 1" class="text-mcdonalds-yellow font-bold">{{ item.quantity }}&times; </span>{{ getLocalizedName(item, language) }}
            </p>
            <p class="text-mcdonalds-yellow text-sm font-bold">
              ${{ (item.price * (item.quantity || 1)).toFixed(2) }}
            </p>
          </div>
        </div>
        <button
          @click="emit('remove', item.id)"
          class="text-white/40 hover:text-red-400 transition-colors p-1 shrink-0"
          title="Remove from order"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none"
               viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round"
                  d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </li>
    </ul>

    <!-- Total -->
    <div
      v-if="items.length"
      class="mt-4 pt-3 border-t border-white/20 flex justify-between items-center"
    >
      <span class="text-white font-semibold">Total</span>
      <span class="text-mcdonalds-yellow font-bold text-lg">
        ${{ total.toFixed(2) }}
      </span>
    </div>
  </div>
</template>
