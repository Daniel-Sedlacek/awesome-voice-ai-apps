/**
 * Audio Recorder for Psychotherapy Tracker Application
 * Handles browser microphone capture with 30-second max duration
 */

// Global state
window.audioRecorder = {
    mediaRecorder: null,
    audioChunks: [],
    isRecording: false,
    startTime: null,
    maxDuration: 30000,  // 30 seconds
    timeoutId: null
};

/**
 * Convert audio blob to base64
 */
async function blobToBase64(blob) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => {
            const base64 = reader.result.split(',')[1];
            resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(blob);
    });
}

/**
 * Convert audio blob to WAV format
 */
async function convertToWav(audioBlob) {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const arrayBuffer = await audioBlob.arrayBuffer();
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

    const wavBuffer = await audioBufferToWav(audioBuffer);
    await audioContext.close();
    return new Blob([wavBuffer], { type: 'audio/wav' });
}

/**
 * Convert AudioBuffer to WAV ArrayBuffer with resampling to 16kHz
 */
async function audioBufferToWav(audioBuffer) {
    const numChannels = 1;
    const targetSampleRate = 16000;
    const bitsPerSample = 16;

    // Resample to 16kHz mono using OfflineAudioContext
    const targetLength = Math.ceil(audioBuffer.duration * targetSampleRate);
    const offlineContext = new OfflineAudioContext(numChannels, targetLength, targetSampleRate);
    const source = offlineContext.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(offlineContext.destination);
    source.start();

    const resampledBuffer = await offlineContext.startRendering();

    const length = resampledBuffer.length;
    const buffer = new ArrayBuffer(44 + length * 2);
    const view = new DataView(buffer);

    // WAV header
    writeString(view, 0, 'RIFF');
    view.setUint32(4, 36 + length * 2, true);
    writeString(view, 8, 'WAVE');
    writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, numChannels, true);
    view.setUint32(24, targetSampleRate, true);
    view.setUint32(28, targetSampleRate * numChannels * bitsPerSample / 8, true);
    view.setUint16(32, numChannels * bitsPerSample / 8, true);
    view.setUint16(34, bitsPerSample, true);
    writeString(view, 36, 'data');
    view.setUint32(40, length * 2, true);

    // Convert float samples to 16-bit PCM
    const channelData = resampledBuffer.getChannelData(0);
    let offset = 44;
    for (let i = 0; i < length; i++) {
        const sample = Math.max(-1, Math.min(1, channelData[i]));
        view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
        offset += 2;
    }

    return buffer;
}

function writeString(view, offset, string) {
    for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
    }
}

/**
 * Start recording from microphone
 */
async function startRecording() {
    if (window.audioRecorder.isRecording) {
        console.log('Already recording');
        return { success: false, error: 'Already recording' };
    }

    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: {
                channelCount: 1,
                sampleRate: 16000,
                echoCancellation: true,
                noiseSuppression: true
            }
        });

        window.audioRecorder.audioChunks = [];
        window.audioRecorder.mediaRecorder = new MediaRecorder(stream, {
            mimeType: MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
                ? 'audio/webm;codecs=opus'
                : 'audio/webm'
        });

        window.audioRecorder.mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                window.audioRecorder.audioChunks.push(event.data);
            }
        };

        window.audioRecorder.mediaRecorder.start(100);
        window.audioRecorder.isRecording = true;
        window.audioRecorder.startTime = Date.now();

        // Auto-stop after max duration
        window.audioRecorder.timeoutId = setTimeout(() => {
            if (window.audioRecorder.isRecording) {
                console.log('Max duration reached, auto-stopping');
                // Just stop the media recorder, the onstop handler will process
                if (window.audioRecorder.mediaRecorder && window.audioRecorder.mediaRecorder.state === 'recording') {
                    window.audioRecorder.mediaRecorder.stop();
                }
            }
        }, window.audioRecorder.maxDuration);

        console.log('Recording started');
        return { success: true };

    } catch (error) {
        console.error('Failed to start recording:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Stop recording and return audio data
 */
async function stopRecording() {
    if (!window.audioRecorder.isRecording || !window.audioRecorder.mediaRecorder) {
        console.log('Not recording');
        return { success: false, error: 'Not recording' };
    }

    // Clear the auto-stop timeout
    if (window.audioRecorder.timeoutId) {
        clearTimeout(window.audioRecorder.timeoutId);
        window.audioRecorder.timeoutId = null;
    }

    return new Promise((resolve) => {
        window.audioRecorder.mediaRecorder.onstop = async () => {
            try {
                const audioBlob = new Blob(window.audioRecorder.audioChunks, { type: 'audio/webm' });

                // Convert to WAV
                const wavBlob = await convertToWav(audioBlob);
                const base64Audio = await blobToBase64(wavBlob);

                // Stop all tracks
                window.audioRecorder.mediaRecorder.stream.getTracks().forEach(track => track.stop());

                window.audioRecorder.isRecording = false;
                window.audioRecorder.audioChunks = [];

                const duration = (Date.now() - window.audioRecorder.startTime) / 1000;
                console.log('Recording stopped, duration:', duration, 'seconds');

                resolve({
                    success: true,
                    audioData: base64Audio,
                    duration: duration
                });
            } catch (error) {
                console.error('Error processing recording:', error);
                window.audioRecorder.isRecording = false;
                resolve({ success: false, error: error.message });
            }
        };

        window.audioRecorder.mediaRecorder.stop();
    });
}

/**
 * Get recording state
 */
function getRecordingState() {
    const elapsed = window.audioRecorder.isRecording
        ? (Date.now() - window.audioRecorder.startTime) / 1000
        : 0;

    const remaining = window.audioRecorder.isRecording
        ? Math.max(0, (window.audioRecorder.maxDuration / 1000) - elapsed)
        : 30;

    return {
        isRecording: window.audioRecorder.isRecording,
        elapsed: elapsed,
        remaining: Math.ceil(remaining)
    };
}

// Expose functions globally for Dash clientside callbacks
window.dashAudioRecorder = {
    startRecording,
    stopRecording,
    getRecordingState
};
