import { ref } from 'vue'
import { useAudioRecording } from './useAudioRecording'

export function useWebSocketAudio() {
  const isConnected = ref(false)
  const isListening = ref(false)
  const interimTranscript = ref('')

  const { isStreaming, error, startStreaming, stopStreaming } = useAudioRecording()

  let ws = null
  let onResults = null
  let onProcessing = null

  function connect(sessionId, language, { onResults: resultsCb, onProcessing: processingCb } = {}) {
    return new Promise((resolve, reject) => {
      onResults = resultsCb || null
      onProcessing = processingCb || null

      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const host = window.location.hostname
      const wsUrl = `${protocol}//${host}:8000/ws/audio`

      ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        ws.send(JSON.stringify({
          type: 'start',
          session_id: sessionId,
          language: language,
        }))
      }

      ws.onmessage = (event) => {
        const msg = JSON.parse(event.data)

        switch (msg.type) {
          case 'connected':
            isConnected.value = true
            resolve(msg.session_id)
            break

          case 'interim':
            interimTranscript.value = msg.text
            break

          case 'processing':
            interimTranscript.value = msg.text
            if (onProcessing) onProcessing(msg.text)
            break

          case 'results':
            interimTranscript.value = ''
            if (onResults) onResults(msg)
            break

          case 'ready':
            // STT is ready for the next utterance
            break

          case 'error':
            console.error('WS error:', msg.message)
            break
        }
      }

      ws.onerror = (err) => {
        console.error('WebSocket error:', err)
        isConnected.value = false
        reject(err)
      }

      ws.onclose = () => {
        isConnected.value = false
        isListening.value = false
      }
    })
  }

  async function startListening() {
    if (!ws || ws.readyState !== WebSocket.OPEN) return

    await startStreaming((pcmBuffer) => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        const bytes = new Uint8Array(pcmBuffer)
        const binary = Array.from(bytes, b => String.fromCharCode(b)).join('')
        ws.send(JSON.stringify({ type: 'audio', data: btoa(binary) }))
      }
    })
    isListening.value = true
  }

  async function stopListening() {
    await stopStreaming()
    isListening.value = false
    interimTranscript.value = ''

    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'stop' }))
    }
  }

  function disconnect() {
    stopStreaming()
    isListening.value = false
    isConnected.value = false
    interimTranscript.value = ''

    if (ws) {
      ws.close()
      ws = null
    }
  }

  return {
    isConnected,
    isListening,
    isStreaming,
    interimTranscript,
    error,
    connect,
    startListening,
    stopListening,
    disconnect,
  }
}
