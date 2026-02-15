<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  label: { type: String, required: true },
  text: { type: String, required: true },
  locale: { type: String, default: '' },
  audioBase64: { type: String, default: '' },
  autoPlay: { type: Boolean, default: false },
})

const emit = defineEmits(['played'])

const isPlaying = ref(false)

function playAudio() {
  if (!props.audioBase64 || isPlaying.value) return
  isPlaying.value = true
  const audio = new Audio(`data:audio/wav;base64,${props.audioBase64}`)
  audio.onended = () => {
    isPlaying.value = false
    emit('played')
  }
  audio.onerror = () => {
    isPlaying.value = false
    emit('played')
  }
  audio.play()
}

watch(() => props.autoPlay, (val) => {
  if (val) playAudio()
})

defineExpose({ playAudio })
</script>

<template>
  <div class="bg-white/10 rounded-xl p-4 flex items-start gap-3">
    <div class="flex-1">
      <p class="text-transport-light text-sm font-semibold mb-1">{{ label }}</p>
      <p class="text-white text-lg">{{ text }}</p>
      <p v-if="locale" class="text-white/40 text-xs mt-1">{{ locale }}</p>
    </div>
    <button
      v-if="audioBase64"
      @click="playAudio"
      :disabled="isPlaying"
      class="mt-1 w-10 h-10 rounded-full flex items-center justify-center transition-all shrink-0"
      :class="isPlaying
        ? 'bg-transport-light/30 text-white animate-pulse'
        : 'bg-transport-light text-transport-blue hover:bg-blue-300 active:scale-95'"
    >
      <svg v-if="!isPlaying" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
        <path d="M8 5v14l11-7z"/>
      </svg>
      <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
        <path d="M6 19h4V5H6zm8-14v14h4V5z"/>
      </svg>
    </button>
  </div>
</template>
