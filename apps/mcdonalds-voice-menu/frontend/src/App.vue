<script setup>
import { useSession } from '@/composables/useSession'
import { processAudio, addToBasket, removeFromBasket } from '@/api/client'
import LanguageSelector from '@/components/LanguageSelector.vue'
import AudioRecorder from '@/components/AudioRecorder.vue'
import MenuGrid from '@/components/MenuGrid.vue'
import BasketPanel from '@/components/BasketPanel.vue'

const {
  sessionId,
  language,
  transcript,
  message,
  menuItems,
  basketItems,
  basketTotal,
  isProcessing,
  supportedLanguages,
  updateFromResponse,
  updateBasketFromResponse,
} = useSession()

async function handleRecorded(audioBlob) {
  isProcessing.value = true
  message.value = ''
  try {
    const response = await processAudio(audioBlob, sessionId.value, language.value)
    updateFromResponse(response)
  } catch (err) {
    message.value = 'Failed to process audio. Please try again.'
    console.error('Audio processing error:', err)
  } finally {
    isProcessing.value = false
  }
}

async function handleAddToBasket(itemId) {
  if (!sessionId.value) return
  try {
    const response = await addToBasket(sessionId.value, itemId)
    updateBasketFromResponse(response)
    menuItems.value = menuItems.value.filter(item => item.id !== itemId)
  } catch (err) {
    message.value = 'Failed to add item to order.'
    console.error('Add to basket error:', err)
  }
}

async function handleRemoveFromBasket(itemId) {
  if (!sessionId.value) return
  try {
    const response = await removeFromBasket(sessionId.value, itemId)
    updateBasketFromResponse(response)
  } catch (err) {
    message.value = 'Failed to remove item from order.'
    console.error('Remove from basket error:', err)
  }
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-b from-mcdonalds-red to-red-900">
    <!-- Header -->
    <header class="py-6 px-4 text-center">
      <h1 class="text-4xl font-bold text-mcdonalds-yellow mb-2">McDonald's</h1>
      <p class="text-white/80 text-lg">Voice Menu</p>
    </header>

    <!-- Controls -->
    <div class="flex flex-col items-center gap-6 px-4 pb-6">
      <LanguageSelector
        v-model="language"
        :languages="supportedLanguages"
      />
      <AudioRecorder
        :disabled="isProcessing"
        @recorded="handleRecorded"
      />
      <p v-if="isProcessing" class="text-mcdonalds-yellow animate-pulse">Processing...</p>
      <p v-if="transcript" class="text-white/90 text-center max-w-md">
        "{{ transcript }}"
      </p>
      <p v-if="message" class="text-mcdonalds-yellow text-center">{{ message }}</p>
    </div>

    <!-- Main Content: Search Results + Basket -->
    <main class="px-4 pb-12 max-w-7xl mx-auto">
      <div class="flex flex-col lg:flex-row gap-6">
        <!-- Search Results -->
        <div class="flex-1 min-w-0">
          <MenuGrid
            :items="menuItems"
            :language="language"
            @add-to-basket="handleAddToBasket"
          />
        </div>

        <!-- Basket Panel -->
        <div class="lg:w-80 shrink-0">
          <div class="lg:sticky lg:top-4">
            <BasketPanel
              :items="basketItems"
              :language="language"
              :total="basketTotal"
              @remove="handleRemoveFromBasket"
            />
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
