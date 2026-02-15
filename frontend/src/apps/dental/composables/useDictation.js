import { ref } from 'vue'
import { dental } from '@/api/client'

export function useDictation() {
  const isProcessing = ref(false)
  const error = ref(null)
  const transcription = ref('')
  const examData = ref(null)
  const extractionNotes = ref(null)

  async function processAudio(audioBase64, locale) {
    isProcessing.value = true
    error.value = null
    transcription.value = ''
    examData.value = null
    extractionNotes.value = null

    try {
      const response = await dental.processAudio(audioBase64, locale)
      transcription.value = response.transcription
      examData.value = response.exam_data
      extractionNotes.value = response.extraction_notes
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Processing failed'
      console.error('Dictation error:', err)
    } finally {
      isProcessing.value = false
    }
  }

  function clear() {
    transcription.value = ''
    examData.value = null
    extractionNotes.value = null
    error.value = null
  }

  return {
    isProcessing,
    error,
    transcription,
    examData,
    extractionNotes,
    processAudio,
    clear,
  }
}
