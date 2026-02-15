<script setup>
import { ref } from 'vue'

const props = defineProps({
  audioSegments: {
    type: Array,
    required: true,
    // Each item: { label: string, audioBase64: string }
  },
  delay: {
    type: Number,
    default: 1500,
  },
})

const isPlaying = ref(false)
const currentIndex = ref(-1)

function playBase64Audio(base64) {
  return new Promise((resolve, reject) => {
    const audio = new Audio(`data:audio/wav;base64,${base64}`)
    audio.onended = resolve
    audio.onerror = reject
    audio.play()
  })
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

async function playAll() {
  if (isPlaying.value) return
  isPlaying.value = true

  try {
    for (let i = 0; i < props.audioSegments.length; i++) {
      currentIndex.value = i
      await playBase64Audio(props.audioSegments[i].audioBase64)
      if (i < props.audioSegments.length - 1) {
        await sleep(props.delay)
      }
    }
  } catch (err) {
    console.error('Audio playback error:', err)
  } finally {
    isPlaying.value = false
    currentIndex.value = -1
  }
}
</script>

<template>
  <button
    @click="playAll"
    :disabled="isPlaying"
    class="px-6 py-3 rounded-xl font-semibold transition-all"
    :class="isPlaying
      ? 'bg-transport-light/30 text-white animate-pulse cursor-not-allowed'
      : 'bg-transport-light text-transport-blue hover:bg-blue-300 active:scale-95'"
  >
    <span v-if="isPlaying">
      Playing {{ audioSegments[currentIndex]?.label || '...' }}
    </span>
    <span v-else>Play All Audio</span>
  </button>
</template>
