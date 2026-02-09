<script setup>
import { watch } from 'vue'
import { useAudioRecording } from '@/composables/useAudioRecording'

defineProps({
  disabled: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['recorded'])

const { isRecording, audioBlob, error, startRecording, stopRecording } = useAudioRecording()

watch(audioBlob, (blob) => {
  if (blob) {
    emit('recorded', blob)
  }
})
</script>

<template>
  <div class="flex flex-col items-center gap-3">
    <button
      @mousedown="startRecording"
      @mouseup="stopRecording"
      @touchstart.prevent="startRecording"
      @touchend.prevent="stopRecording"
      :disabled="disabled"
      class="w-20 h-20 rounded-full flex items-center justify-center transition-all duration-200 select-none"
      :class="[
        isRecording
          ? 'bg-mcdonalds-red scale-110 shadow-lg shadow-red-500/50 animate-pulse'
          : disabled
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-mcdonalds-yellow hover:scale-105 hover:shadow-lg active:scale-95',
      ]"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="w-8 h-8"
        :class="isRecording ? 'text-white' : 'text-mcdonalds-red'"
        viewBox="0 0 24 24"
        fill="currentColor"
      >
        <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
        <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
      </svg>
    </button>
    <p class="text-sm text-white/70">
      {{ isRecording ? 'Listening...' : 'Hold to speak' }}
    </p>
    <p v-if="error" class="text-sm text-red-400">{{ error }}</p>
  </div>
</template>
