import { ref } from 'vue'
import { psychotherapy } from '@/api/client'

export function useTracker() {
  const isProcessing = ref(false)
  const error = ref(null)
  const currentSession = ref(null)
  const sessions = ref([])
  const sessionCount = ref(0)

  async function processAudio(audioBase64, locale) {
    isProcessing.value = true
    error.value = null

    try {
      const response = await psychotherapy.processAudio(audioBase64, locale)
      currentSession.value = response.session
      sessionCount.value = response.session_count
      // Refresh sessions list
      await fetchSessions()
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Analysis failed'
      console.error('Tracker error:', err)
    } finally {
      isProcessing.value = false
    }
  }

  async function fetchSessions() {
    try {
      const response = await psychotherapy.getSessions()
      sessions.value = response.sessions
      sessionCount.value = response.sessions.length
    } catch (err) {
      console.error('Fetch sessions error:', err)
    }
  }

  return {
    isProcessing,
    error,
    currentSession,
    sessions,
    sessionCount,
    processAudio,
    fetchSessions,
  }
}
