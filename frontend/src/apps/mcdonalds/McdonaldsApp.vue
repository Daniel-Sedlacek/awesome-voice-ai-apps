<script setup>
import { ref } from 'vue'
import { useSession } from './composables/useSession'
import { useWebSocketAudio } from '@/shared/composables/useWebSocketAudio'
import { mcdonalds } from '@/api/client'
import LanguageSelector from '@/shared/components/LanguageSelector.vue'
import AudioRecorder from '@/shared/components/AudioRecorder.vue'
import MenuGrid from './components/MenuGrid.vue'
import BasketPanel from './components/BasketPanel.vue'

const showHints = ref(false)

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
} = useWebSocketAudio('/ws/mcdonalds/audio')

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
    const response = await mcdonalds.addToBasket(sessionId.value, itemId)
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
    const response = await mcdonalds.removeFromBasket(sessionId.value, itemId)
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

      <!-- Voice Command Hints -->
      <div class="w-full max-w-lg">
        <button
          class="text-white/60 hover:text-white/90 text-sm flex items-center gap-1 mx-auto transition-colors cursor-pointer"
          @click="showHints = !showHints"
        >
          <svg
            class="w-4 h-4 transition-transform"
            :class="{ 'rotate-180': showHints }"
            fill="none" viewBox="0 0 24 24" stroke="currentColor"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
          What can I say?
        </button>
        <Transition name="hints">
          <div v-if="showHints" class="mt-3 bg-black/30 rounded-xl p-4 text-sm text-white/80 space-y-3">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <p class="text-mcdonalds-yellow font-semibold mb-1">Search menu</p>
                <p class="text-white/60 italic">"I want a burger"</p>
                <p class="text-white/60 italic">"Show me drinks"</p>
              </div>
              <div>
                <p class="text-mcdonalds-yellow font-semibold mb-1">Refine search</p>
                <p class="text-white/60 italic">"With cheese"</p>
                <p class="text-white/60 italic">"Something cold"</p>
              </div>
              <div>
                <p class="text-mcdonalds-yellow font-semibold mb-1">Add to order</p>
                <p class="text-white/60 italic">"I'll take the Big Mac"</p>
                <p class="text-white/60 italic">"Add the McFlurry"</p>
              </div>
              <div>
                <p class="text-mcdonalds-yellow font-semibold mb-1">Remove from results</p>
                <p class="text-white/60 italic">"Remove the salad"</p>
              </div>
              <div>
                <p class="text-mcdonalds-yellow font-semibold mb-1">Remove from order</p>
                <p class="text-white/60 italic">"Take the fries off my order"</p>
              </div>
              <div>
                <p class="text-mcdonalds-yellow font-semibold mb-1">Start over / Confirm</p>
                <p class="text-white/60 italic">"Clear everything"</p>
                <p class="text-white/60 italic">"I'm done"</p>
              </div>
            </div>
          </div>
        </Transition>
      </div>
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

<style scoped>
.hints-enter-active,
.hints-leave-active {
  transition: all 0.25s ease;
  overflow: hidden;
}
.hints-enter-from,
.hints-leave-to {
  opacity: 0;
  max-height: 0;
}
.hints-enter-to,
.hints-leave-from {
  opacity: 1;
  max-height: 300px;
}
</style>
