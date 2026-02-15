<script setup>
import { ref, watch, nextTick } from 'vue'
import { useAudioRecording } from '@/shared/composables/useAudioRecording'
import { useTranslation } from './composables/useTranslation'
import LanguageSelector from '@/shared/components/LanguageSelector.vue'
import AudioRecorder from '@/shared/components/AudioRecorder.vue'
import TranslationResult from './components/TranslationResult.vue'

const languages = [
  { code: 'en-US', label: 'English (US)', flag: '\u{1f1fa}\u{1f1f8}' },
  { code: 'en-GB', label: 'English (UK)', flag: '\u{1f1ec}\u{1f1e7}' },
  { code: 'es-ES', label: 'Spanish', flag: '\u{1f1ea}\u{1f1f8}' },
  { code: 'fr-FR', label: 'French', flag: '\u{1f1eb}\u{1f1f7}' },
  { code: 'de-DE', label: 'German', flag: '\u{1f1e9}\u{1f1ea}' },
  { code: 'it-IT', label: 'Italian', flag: '\u{1f1ee}\u{1f1f9}' },
  { code: 'pt-BR', label: 'Portuguese', flag: '\u{1f1e7}\u{1f1f7}' },
  { code: 'zh-CN', label: 'Chinese', flag: '\u{1f1e8}\u{1f1f3}' },
  { code: 'ja-JP', label: 'Japanese', flag: '\u{1f1ef}\u{1f1f5}' },
  { code: 'ko-KR', label: 'Korean', flag: '\u{1f1f0}\u{1f1f7}' },
  { code: 'ru-RU', label: 'Russian', flag: '\u{1f1f7}\u{1f1fa}' },
  { code: 'ar-SA', label: 'Arabic', flag: '\u{1f1f8}\u{1f1e6}' },
  { code: 'hi-IN', label: 'Hindi', flag: '\u{1f1ee}\u{1f1f3}' },
  { code: 'pl-PL', label: 'Polish', flag: '\u{1f1f5}\u{1f1f1}' },
]

const sourceLocale = ref('en-US')
const targetLocale1 = ref('de-DE')
const targetLocale2 = ref('es-ES')

const { isRecording, audioBlob, error: recError, startRecording, stopRecording } = useAudioRecording()
const { isProcessing, error: apiError, result, processAudio } = useTranslation()

// Watch for recording completion and auto-process
watch(audioBlob, async (blob) => {
  if (!blob) return
  const reader = new FileReader()
  reader.onloadend = async () => {
    const base64 = reader.result.split(',')[1]
    await processAudio(base64, sourceLocale.value, targetLocale1.value, targetLocale2.value)
  }
  reader.readAsDataURL(blob)
})

const autoPlayIndex = ref(-1)

watch(result, async (r) => {
  if (!r) return
  autoPlayIndex.value = -1
  await nextTick()
  autoPlayIndex.value = 0
})

function onSegmentPlayed(index) {
  if (index < 2) {
    autoPlayIndex.value = index + 1
  } else {
    autoPlayIndex.value = -1
  }
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-b from-transport-blue to-blue-900">
    <header class="py-6 px-4 text-center">
      <h1 class="text-4xl font-bold text-transport-light mb-2">Public Transport Voice</h1>
      <p class="text-white/80 text-lg">Speak, Translate, Listen</p>
    </header>

    <div class="max-w-2xl mx-auto px-4 pb-12 space-y-8">
      <!-- Language selectors -->
      <div class="space-y-4">
        <div>
          <label class="text-transport-light text-sm font-semibold mb-2 block">Source Language</label>
          <LanguageSelector
            v-model="sourceLocale"
            :languages="languages"
            active-class="bg-transport-light text-transport-blue shadow-md scale-105"
          />
        </div>
        <div>
          <label class="text-transport-light text-sm font-semibold mb-2 block">Target Language 1</label>
          <LanguageSelector
            v-model="targetLocale1"
            :languages="languages"
            active-class="bg-transport-light text-transport-blue shadow-md scale-105"
          />
        </div>
        <div>
          <label class="text-transport-light text-sm font-semibold mb-2 block">Target Language 2</label>
          <LanguageSelector
            v-model="targetLocale2"
            :languages="languages"
            active-class="bg-transport-light text-transport-blue shadow-md scale-105"
          />
        </div>
      </div>

      <!-- Recorder -->
      <div class="flex flex-col items-center gap-4">
        <AudioRecorder
          mode="oneshot"
          :is-recording="isRecording"
          :disabled="isProcessing"
          active-color="bg-transport-light"
          pulse-color="bg-red-500"
          icon-color="text-transport-blue"
          start-label="Record message"
          stop-label="Stop recording"
          @start="startRecording"
          @stop="stopRecording"
        />
        <p v-if="isProcessing" class="text-transport-light animate-pulse">Translating...</p>
        <p v-if="recError" class="text-red-400 text-sm">{{ recError }}</p>
        <p v-if="apiError" class="text-red-400 text-sm">{{ apiError }}</p>
      </div>

      <!-- Results -->
      <div v-if="result" class="space-y-4">
        <TranslationResult
          label="Original"
          :text="result.original.text"
          :locale="result.original.locale"
          :audio-base64="result.original.audio_base64"
          :auto-play="autoPlayIndex === 0"
          @played="onSegmentPlayed(0)"
        />
        <TranslationResult
          label="Translation 1"
          :text="result.translation_1.text"
          :locale="result.translation_1.locale"
          :audio-base64="result.translation_1.audio_base64"
          :auto-play="autoPlayIndex === 1"
          @played="onSegmentPlayed(1)"
        />
        <TranslationResult
          label="Translation 2"
          :text="result.translation_2.text"
          :locale="result.translation_2.locale"
          :audio-base64="result.translation_2.audio_base64"
          :auto-play="autoPlayIndex === 2"
          @played="onSegmentPlayed(2)"
        />
      </div>
    </div>
  </div>
</template>
