<script setup>
import { useSession } from '@/composables/useSession'
import { processAudio } from '@/api/client'
import LanguageSelector from '@/components/LanguageSelector.vue'
import AudioRecorder from '@/components/AudioRecorder.vue'
import MenuGrid from '@/components/MenuGrid.vue'

const {
  sessionId,
  language,
  transcript,
  message,
  menuItems,
  isProcessing,
  supportedLanguages,
  updateFromResponse,
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

    <!-- Menu Results -->
    <main class="px-4 pb-12 max-w-7xl mx-auto">
      <MenuGrid :items="menuItems" :language="language" />
    </main>
  </div>
</template>
