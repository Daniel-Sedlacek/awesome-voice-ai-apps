import { ref, onUnmounted } from 'vue'

export function useAudioRecording() {
  const isRecording = ref(false)
  const audioBlob = ref(null)
  const error = ref(null)

  const isStreaming = ref(false)

  let mediaRecorder = null
  let audioChunks = []
  let stream = null

  // Streaming mode state
  let streamingContext = null
  let streamingSource = null
  let workletNode = null
  let streamingStream = null

  function getSupportedMimeType() {
    const types = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/mp4',
      'audio/ogg;codecs=opus',
      'audio/wav',
    ]
    for (const type of types) {
      if (MediaRecorder.isTypeSupported(type)) {
        return type
      }
    }
    return ''
  }

  async function startRecording() {
    try {
      error.value = null
      audioBlob.value = null
      audioChunks = []

      stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000,
        },
      })

      const mimeType = getSupportedMimeType()
      const options = mimeType ? { mimeType } : {}

      mediaRecorder = new MediaRecorder(stream, options)

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.push(event.data)
        }
      }

      mediaRecorder.onstop = async () => {
        const blob = new Blob(audioChunks, { type: mimeType || 'audio/webm' })
        audioBlob.value = await convertToWav(blob)
      }

      mediaRecorder.start()
      isRecording.value = true
    } catch (err) {
      error.value = err.message
      console.error('Failed to start recording:', err)
    }
  }

  async function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop()
      stream?.getTracks().forEach((track) => track.stop())
      isRecording.value = false
    }
  }

  async function convertToWav(blob) {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext
    const audioContext = new AudioContextClass()

    if (audioContext.state === 'suspended') {
      await audioContext.resume()
    }

    const arrayBuffer = await blob.arrayBuffer()
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer)

    const targetSampleRate = 16000
    const offlineContext = new OfflineAudioContext(
      1,
      audioBuffer.duration * targetSampleRate,
      targetSampleRate,
    )

    const source = offlineContext.createBufferSource()
    source.buffer = audioBuffer
    source.connect(offlineContext.destination)
    source.start()

    const renderedBuffer = await offlineContext.startRendering()
    const wavBlob = encodeWav(renderedBuffer)
    await audioContext.close()

    return wavBlob
  }

  function encodeWav(audioBuffer) {
    const numChannels = 1
    const sampleRate = audioBuffer.sampleRate
    const format = 1 // PCM
    const bitsPerSample = 16

    const samples = audioBuffer.getChannelData(0)
    const buffer = new ArrayBuffer(44 + samples.length * 2)
    const view = new DataView(buffer)

    writeString(view, 0, 'RIFF')
    view.setUint32(4, 36 + samples.length * 2, true)
    writeString(view, 8, 'WAVE')
    writeString(view, 12, 'fmt ')
    view.setUint32(16, 16, true)
    view.setUint16(20, format, true)
    view.setUint16(22, numChannels, true)
    view.setUint32(24, sampleRate, true)
    view.setUint32(28, (sampleRate * numChannels * bitsPerSample) / 8, true)
    view.setUint16(32, (numChannels * bitsPerSample) / 8, true)
    view.setUint16(34, bitsPerSample, true)
    writeString(view, 36, 'data')
    view.setUint32(40, samples.length * 2, true)

    let offset = 44
    for (let i = 0; i < samples.length; i++) {
      const s = Math.max(-1, Math.min(1, samples[i]))
      view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true)
      offset += 2
    }

    return new Blob([buffer], { type: 'audio/wav' })
  }

  function writeString(view, offset, string) {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i))
    }
  }

  async function startStreaming(onChunk) {
    try {
      error.value = null
      streamingStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
        },
      })

      streamingContext = new AudioContext()

      if (streamingContext.state === 'suspended') {
        await streamingContext.resume()
      }

      await streamingContext.audioWorklet.addModule('/pcm-processor.js')

      streamingSource = streamingContext.createMediaStreamSource(streamingStream)
      workletNode = new AudioWorkletNode(streamingContext, 'pcm-processor')

      workletNode.port.onmessage = (event) => {
        onChunk(event.data)
      }

      streamingSource.connect(workletNode)
      workletNode.connect(streamingContext.destination)
      isStreaming.value = true
    } catch (err) {
      error.value = err.message
      console.error('Failed to start streaming:', err)
    }
  }

  async function stopStreaming() {
    if (workletNode) {
      workletNode.disconnect()
      workletNode = null
    }
    if (streamingSource) {
      streamingSource.disconnect()
      streamingSource = null
    }
    if (streamingStream) {
      streamingStream.getTracks().forEach((track) => track.stop())
      streamingStream = null
    }
    if (streamingContext) {
      await streamingContext.close()
      streamingContext = null
    }
    isStreaming.value = false
  }

  onUnmounted(() => {
    stopRecording()
    stopStreaming()
  })

  return {
    isRecording,
    isStreaming,
    audioBlob,
    error,
    startRecording,
    stopRecording,
    startStreaming,
    stopStreaming,
  }
}
