import { ref } from 'vue'
import { transport } from '@/api/client'

export function useTranslation() {
  const isProcessing = ref(false)
  const error = ref(null)
  const result = ref(null)

  async function processAudio(audioBase64, sourceLocale, targetLocale1, targetLocale2) {
    isProcessing.value = true
    error.value = null
    result.value = null

    try {
      const response = await transport.processAudio(
        audioBase64, sourceLocale, targetLocale1, targetLocale2
      )
      result.value = response
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Processing failed'
      console.error('Translation error:', err)
    } finally {
      isProcessing.value = false
    }
  }

  function clear() {
    result.value = null
    error.value = null
  }

  return {
    isProcessing,
    error,
    result,
    processAudio,
    clear,
  }
}
