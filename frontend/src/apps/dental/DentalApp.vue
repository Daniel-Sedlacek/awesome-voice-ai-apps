<script setup>
import { ref, watch } from 'vue'
import { useAudioRecording } from '@/shared/composables/useAudioRecording'
import { useDictation } from './composables/useDictation'
import LanguageSelector from '@/shared/components/LanguageSelector.vue'
import AudioRecorder from '@/shared/components/AudioRecorder.vue'
import DentalChart from './components/DentalChart.vue'
import ExamSummary from './components/ExamSummary.vue'

const languages = [
  { code: 'en-US', label: 'English', flag: '\u{1f1ec}\u{1f1e7}' },
  { code: 'de-DE', label: 'Deutsch', flag: '\u{1f1e9}\u{1f1ea}' },
  { code: 'cs-CZ', label: '\u010ce\u0161tina', flag: '\u{1f1e8}\u{1f1ff}' },
]

const locale = ref('en-US')

const { isRecording, audioBlob, error: recError, startRecording, stopRecording } = useAudioRecording()
const { isProcessing, error: apiError, transcription, examData, extractionNotes, processAudio } = useDictation()

watch(audioBlob, async (blob) => {
  if (!blob) return
  const reader = new FileReader()
  reader.onloadend = async () => {
    const base64 = reader.result.split(',')[1]
    await processAudio(base64, locale.value)
  }
  reader.readAsDataURL(blob)
})
</script>

<template>
  <div class="min-h-screen bg-gradient-to-b from-dental-teal to-teal-900">
    <header class="py-6 px-4 text-center">
      <h1 class="text-4xl font-bold text-dental-light mb-2">Dental Dictation</h1>
      <p class="text-white/80 text-lg">Dictate periodontal exam findings</p>
    </header>

    <div class="max-w-3xl mx-auto px-4 pb-12 space-y-8">
      <!-- Language selector -->
      <div class="flex justify-center">
        <LanguageSelector
          v-model="locale"
          :languages="languages"
          active-class="bg-dental-light text-dental-teal shadow-md scale-105"
        />
      </div>

      <!-- Recorder -->
      <div class="flex flex-col items-center gap-4">
        <AudioRecorder
          mode="oneshot"
          :is-recording="isRecording"
          :disabled="isProcessing"
          active-color="bg-dental-light"
          pulse-color="bg-red-500"
          icon-color="text-dental-teal"
          start-label="Start dictation"
          stop-label="Stop dictation"
          @start="startRecording"
          @stop="stopRecording"
        />
        <p v-if="isProcessing" class="text-dental-light animate-pulse">Extracting dental data...</p>
        <p v-if="recError" class="text-red-400 text-sm">{{ recError }}</p>
        <p v-if="apiError" class="text-red-400 text-sm">{{ apiError }}</p>
      </div>

      <!-- Results -->
      <div v-if="examData" class="space-y-6">
        <DentalChart :exam-data="examData" />
        <ExamSummary
          :exam-data="examData"
          :transcription="transcription"
          :extraction-notes="extractionNotes"
        />
      </div>
    </div>
  </div>
</template>
