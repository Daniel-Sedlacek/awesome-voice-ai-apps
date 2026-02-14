<script setup>
import { useSession } from '@/composables/useSession'
import { useWebSocketAudio } from '@/composables/useWebSocketAudio'
import { addToBasket, removeFromBasket } from '@/api/client'
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
  interimTranscript,
  isOrdering,
  supportedLanguages,
  updateFromResponse,
  updateBasketFromResponse,
} = useSession()

const {
  isListening,
  interimTranscript: wsInterim,
  connect,
  startListening,
  stopListening,
  disconnect,
  error: audioError,
} = useWebSocketAudio()

async function handleStartOrdering() {
  isProcessing.value = false
  message.value = ''

  try {
    const sid = await connect(sessionId.value, language.value, {
      onResults(msg) {
        updateFromResponse(msg)
        isProcessing.value = false
      },
      onProcessing(text) {
        transcript.value = text
        isProcessing.value = true
      },
    })
    sessionId.value = sid
    isOrdering.value = true
    await startListening()
  } catch (err) {
    message.value = 'Failed to connect. Please try again.'
    console.error('WS connect error:', err)
  }
}

async function handleStopOrdering() {
  await stopListening()
  disconnect()
  isOrdering.value = false
  interimTranscript.value = ''
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
        :disabled="isOrdering"
      />
      <AudioRecorder
        :is-ordering="isOrdering"
        :is-listening="isListening"
        :interim-transcript="wsInterim"
        :disabled="isProcessing && !isOrdering"
        @start="handleStartOrdering"
        @stop="handleStopOrdering"
      />
      <p v-if="isProcessing" class="text-mcdonalds-yellow animate-pulse">Processing...</p>
      <p v-if="transcript && !isProcessing" class="text-white/90 text-center max-w-md">
        "{{ transcript }}"
      </p>
      <p v-if="message" class="text-mcdonalds-yellow text-center">{{ message }}</p>
      <p v-if="audioError" class="text-sm text-red-400">{{ audioError }}</p>
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
