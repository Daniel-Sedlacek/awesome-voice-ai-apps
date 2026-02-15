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
  confirmed: {
    type: Boolean,
    default: false,
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
  <div
    class="backdrop-blur-sm rounded-2xl p-4 transition-all duration-500"
    :class="confirmed ? 'bg-emerald-500/30 ring-2 ring-emerald-400' : 'bg-white/10'"
  >
    <h2
      class="font-bold text-xl mb-4 flex items-center gap-2 transition-colors duration-500"
      :class="confirmed ? 'text-emerald-300' : 'text-mcdonalds-yellow'"
    >
      <svg v-if="!confirmed" xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none"
           viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round"
              d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
      </svg>
      <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none"
           viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round"
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      {{ confirmed ? 'Order Confirmed' : 'My Order' }}
      <span
        v-if="items.length && !confirmed"
        class="bg-mcdonalds-yellow text-mcdonalds-red text-sm rounded-full w-6 h-6 flex items-center justify-center font-bold"
      >
        {{ items.reduce((sum, i) => sum + (i.quantity || 1), 0) }}
      </span>
    </h2>

    <div v-if="items.length === 0" class="text-center py-8">
      <p class="text-white/40 text-sm">
        Say "I'll take the..." or click + to add items
      </p>
    </div>

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
          v-if="!confirmed"
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

    <div
      v-if="items.length"
      class="mt-4 pt-3 border-t transition-colors duration-500"
      :class="confirmed ? 'border-emerald-400/30' : 'border-white/20'"
    >
      <div class="flex justify-between items-center">
        <span class="text-white font-semibold">Total</span>
        <span
          class="font-bold text-lg transition-colors duration-500"
          :class="confirmed ? 'text-emerald-300' : 'text-mcdonalds-yellow'"
        >
          ${{ total.toFixed(2) }}
        </span>
      </div>
      <p
        v-if="confirmed"
        class="mt-3 text-center text-emerald-300 font-semibold text-sm animate-fade-in"
      >
        Order confirmed! Thank you!
      </p>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.5s ease-in;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
