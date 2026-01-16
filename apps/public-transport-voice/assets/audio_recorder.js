/**
 * Audio Recorder for Dash Application
 * Handles browser microphone capture with 10-second limit
 */

// Global state
window.audioRecorder = {
    mediaRecorder: null,
    audioChunks: [],
    isRecording: false,
    recordingTimeout: null,
    maxDuration: 10000,  // 10 seconds in milliseconds
    startTime: null
};

/**
 * Convert audio blob to base64 WAV format
 */
async function blobToBase64(blob) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => {
            // Remove data URL prefix to get pure base64
            const base64 = reader.result.split(',')[1];
            resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(blob);
    });
}

/**
 * Convert audio blob to WAV format
 * The MediaRecorder typically outputs webm/opus, we need WAV for Azure
 */
async function convertToWav(audioBlob) {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const arrayBuffer = await audioBlob.arrayBuffer();
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

    // Create WAV file with proper resampling
    const wavBuffer = await audioBufferToWav(audioBuffer);
    return new Blob([wavBuffer], { type: 'audio/wav' });
}

/**
 * Convert AudioBuffer to WAV ArrayBuffer with proper resampling to 16kHz
 */
async function audioBufferToWav(audioBuffer) {
    const numChannels = 1;  // Mono
    const targetSampleRate = 16000;  // 16kHz for Azure Speech
    const bitsPerSample = 16;

    // Resample to 16kHz mono using OfflineAudioContext
    const targetLength = Math.ceil(audioBuffer.duration * targetSampleRate);
    const offlineContext = new OfflineAudioContext(numChannels, targetLength, targetSampleRate);
    const source = offlineContext.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(offlineContext.destination);
    source.start();

    // Wait for resampling to complete
    const resampledBuffer = await offlineContext.startRendering();

    const length = resampledBuffer.length;
    const buffer = new ArrayBuffer(44 + length * 2);
    const view = new DataView(buffer);

    // WAV header
    writeString(view, 0, 'RIFF');
    view.setUint32(4, 36 + length * 2, true);
    writeString(view, 8, 'WAVE');
    writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true);  // Subchunk1Size
    view.setUint16(20, 1, true);   // AudioFormat (PCM)
    view.setUint16(22, numChannels, true);
    view.setUint32(24, targetSampleRate, true);
    view.setUint32(28, targetSampleRate * numChannels * bitsPerSample / 8, true);
    view.setUint16(32, numChannels * bitsPerSample / 8, true);
    view.setUint16(34, bitsPerSample, true);
    writeString(view, 36, 'data');
    view.setUint32(40, length * 2, true);

    // Convert float samples to 16-bit PCM from the resampled buffer
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

        window.audioRecorder.mediaRecorder.start(100);  // Collect data every 100ms
        window.audioRecorder.isRecording = true;
        window.audioRecorder.startTime = Date.now();

        // Auto-stop after max duration
        window.audioRecorder.recordingTimeout = setTimeout(() => {
            if (window.audioRecorder.isRecording) {
                stopRecording();
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

    return new Promise((resolve) => {
        // Clear the auto-stop timeout
        if (window.audioRecorder.recordingTimeout) {
            clearTimeout(window.audioRecorder.recordingTimeout);
            window.audioRecorder.recordingTimeout = null;
        }

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
        : window.audioRecorder.maxDuration / 1000;

    return {
        isRecording: window.audioRecorder.isRecording,
        elapsed: elapsed,
        remaining: remaining
    };
}

/**
 * Play audio from base64 data with delay
 */
function playAudioSequence(audioDataList, delayMs = 1500) {
    return new Promise((resolve) => {
        let currentIndex = 0;

        function playNext() {
            if (currentIndex >= audioDataList.length) {
                resolve();
                return;
            }

            const audioData = audioDataList[currentIndex];
            const audio = new Audio('data:audio/wav;base64,' + audioData);

            audio.onended = () => {
                currentIndex++;
                if (currentIndex < audioDataList.length) {
                    setTimeout(playNext, delayMs);
                } else {
                    resolve();
                }
            };

            audio.onerror = (e) => {
                console.error('Audio playback error:', e);
                currentIndex++;
                if (currentIndex < audioDataList.length) {
                    setTimeout(playNext, delayMs);
                } else {
                    resolve();
                }
            };

            audio.play().catch(err => {
                console.error('Failed to play audio:', err);
                currentIndex++;
                if (currentIndex < audioDataList.length) {
                    setTimeout(playNext, delayMs);
                } else {
                    resolve();
                }
            });
        }

        playNext();
    });
}

// Expose functions globally for Dash clientside callbacks
window.dashAudioRecorder = {
    startRecording,
    stopRecording,
    getRecordingState,
    playAudioSequence
};
