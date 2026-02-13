import { ref, computed } from 'vue'

export function useSession() {
  const sessionId = ref(null)
  const language = ref('en-US')
  const transcript = ref('')
  const message = ref('')
  const menuItems = ref([])
  const basketItems = ref([])
  const isProcessing = ref(false)

  const supportedLanguages = [
    { code: 'en-US', label: 'English', flag: '\u{1f1ec}\u{1f1e7}' },
    { code: 'de-DE', label: 'Deutsch', flag: '\u{1f1e9}\u{1f1ea}' },
    { code: 'cs-CZ', label: '\u010ce\u0161tina', flag: '\u{1f1e8}\u{1f1ff}' },
  ]

  const basketTotal = computed(() => {
    return basketItems.value.reduce((sum, item) => sum + item.price, 0)
  })

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
    if (response.basket_items !== undefined) {
      basketItems.value = response.basket_items
    }
  }

  function updateBasketFromResponse(response) {
    if (response.session_id) {
      sessionId.value = response.session_id
    }
    if (response.message) {
      message.value = response.message
    }
    basketItems.value = response.basket_items || []
  }

  function clearSession() {
    sessionId.value = null
    transcript.value = ''
    message.value = ''
    menuItems.value = []
    basketItems.value = []
  }

  return {
    sessionId,
    language,
    transcript,
    message,
    menuItems,
    basketItems,
    basketTotal,
    isProcessing,
    supportedLanguages,
    updateFromResponse,
    updateBasketFromResponse,
    clearSession,
  }
}
