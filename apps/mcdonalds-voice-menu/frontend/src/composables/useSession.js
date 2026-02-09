import { ref } from 'vue'

export function useSession() {
  const sessionId = ref(null)
  const language = ref('en-US')
  const transcript = ref('')
  const message = ref('')
  const menuItems = ref([])
  const isProcessing = ref(false)

  const supportedLanguages = [
    { code: 'en-US', label: 'English', flag: '🇬🇧' },
    { code: 'de-DE', label: 'Deutsch', flag: '🇩🇪' },
    { code: 'cs-CZ', label: 'Čeština', flag: '🇨🇿' },
  ]

  function updateFromResponse(response) {
    if (response.session_id) {
      sessionId.value = response.session_id
    }
    if (response.transcript) {
      transcript.value = response.transcript
    }
    if (response.message) {
      message.value = response.message
    }
    menuItems.value = response.items || []
  }

  function clearSession() {
    sessionId.value = null
    transcript.value = ''
    message.value = ''
    menuItems.value = []
  }

  return {
    sessionId,
    language,
    transcript,
    message,
    menuItems,
    isProcessing,
    supportedLanguages,
    updateFromResponse,
    clearSession,
  }
}
