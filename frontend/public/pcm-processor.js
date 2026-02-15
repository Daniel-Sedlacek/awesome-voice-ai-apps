/**
 * AudioWorklet processor that captures raw PCM from the microphone,
 * downsamples to 16 kHz mono, and posts Int16 buffers to the main thread.
 */
class PCMProcessor extends AudioWorkletProcessor {
  constructor() {
    super()
    this._buffer = []
    // sampleRate is the AudioContext sample rate (usually 44100 or 48000)
    this._ratio = sampleRate / 16000
  }

  process(inputs) {
    const input = inputs[0]
    if (!input || !input[0]) return true

    const samples = input[0] // Float32Array, mono channel 0

    // Downsample by picking nearest sample
    for (let i = 0; i < samples.length; i++) {
      this._buffer.push(samples[i])
    }

    // Flush in ~50ms chunks at 16kHz = 800 samples
    const chunkSize = Math.floor(800 * this._ratio)
    while (this._buffer.length >= chunkSize) {
      const raw = this._buffer.splice(0, chunkSize)
      const outLen = Math.floor(raw.length / this._ratio)
      const int16 = new Int16Array(outLen)
      for (let i = 0; i < outLen; i++) {
        const srcIdx = Math.floor(i * this._ratio)
        const s = Math.max(-1, Math.min(1, raw[srcIdx]))
        int16[i] = s < 0 ? s * 0x8000 : s * 0x7fff
      }
      this.port.postMessage(int16.buffer, [int16.buffer])
    }

    return true
  }
}

registerProcessor('pcm-processor', PCMProcessor)
