<script setup>
import { ref, watch, onMounted } from 'vue'
import { useAudioRecording } from '@/shared/composables/useAudioRecording'
import { useTracker } from './composables/useTracker'
import { psychotherapy } from '@/api/client'
import LanguageSelector from '@/shared/components/LanguageSelector.vue'
import AudioRecorder from '@/shared/components/AudioRecorder.vue'
import RadarChart from './components/RadarChart.vue'
import AnalysisReport from './components/AnalysisReport.vue'
import MonologueSelector from './components/MonologueSelector.vue'
import SessionHistory from './components/SessionHistory.vue'

const languages = [
  { code: 'en-US', label: 'English', flag: '\u{1f1ec}\u{1f1e7}' },
  { code: 'de-DE', label: 'Deutsch', flag: '\u{1f1e9}\u{1f1ea}' },
  { code: 'cs-CZ', label: '\u010ce\u0161tina', flag: '\u{1f1e8}\u{1f1ff}' },
]

const locale = ref('en-US')
const selectedMonologue = ref('')
const monologues = ref([])

const { isRecording, audioBlob, error: recError, startRecording, stopRecording } = useAudioRecording()
const { isProcessing, error: apiError, currentSession, sessions, sessionCount, processAudio, fetchSessions } = useTracker()

// Load monologues for current locale
async function loadMonologues() {
  try {
    const response = await psychotherapy.getLanguages()
    const lang = response.languages.find(l => l.locale === locale.value)
    monologues.value = lang?.monologues || []
    selectedMonologue.value = ''
  } catch (err) {
    console.error('Failed to load monologues:', err)
  }
}

watch(locale, loadMonologues)
onMounted(() => {
  loadMonologues()
  fetchSessions()
})

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
  <div class="min-h-screen bg-gradient-to-b from-psych-purple to-purple-900">
    <header class="py-6 px-4 text-center">
      <h1 class="text-4xl font-bold text-psych-light mb-2">Psychotherapy Tracker</h1>
      <p class="text-white/80 text-lg">Track your emotional wellness with voice</p>
    </header>

    <div class="max-w-4xl mx-auto px-4 pb-12 space-y-8">
      <!-- Language selector -->
      <div class="flex justify-center">
        <LanguageSelector
          v-model="locale"
          :languages="languages"
          active-class="bg-psych-light text-psych-purple shadow-md scale-105"
        />
      </div>

      <!-- Monologue selector -->
      <MonologueSelector
        v-if="monologues.length"
        v-model="selectedMonologue"
        :monologues="monologues"
      />

      <!-- Recorder -->
      <div class="flex flex-col items-center gap-4">
        <AudioRecorder
          mode="oneshot"
          :is-recording="isRecording"
          :disabled="isProcessing"
          active-color="bg-psych-light"
          pulse-color="bg-red-500"
          icon-color="text-psych-purple"
          start-label="Start recording"
          stop-label="Stop recording"
          @start="startRecording"
          @stop="stopRecording"
        />
        <p v-if="isProcessing" class="text-psych-light animate-pulse">Analyzing your words...</p>
        <p v-if="sessionCount > 0 && !isProcessing" class="text-white/50 text-sm">
          {{ sessionCount }} session(s) today
        </p>
        <p v-if="recError" class="text-red-400 text-sm">{{ recError }}</p>
        <p v-if="apiError" class="text-red-400 text-sm">{{ apiError }}</p>
      </div>

      <!-- Results -->
      <div v-if="currentSession" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RadarChart :metrics="currentSession.metrics" />
        <AnalysisReport
          :report="currentSession.report"
          :transcription="currentSession.transcription"
        />
      </div>

      <!-- Session history -->
      <SessionHistory :sessions="sessions" />

      <!-- Disclaimer -->
      <p class="text-white/30 text-xs text-center max-w-md mx-auto">
        This is a wellness tool, not a medical device.
        For mental health concerns, please consult a professional.
      </p>
    </div>
  </div>
</template>
