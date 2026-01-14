# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run the application locally
uv run python app.py

# Run with Docker
docker compose up -d --build
```

## Environment Variables

Copy `.env.example` to `.env` and configure:
- `AZURE_SPEECH_KEY` / `AZURE_SPEECH_REGION` - Azure Speech Service
- `AZURE_TRANSLATOR_KEY` / `AZURE_TRANSLATOR_REGION` - Azure Translator
- `HOST` (default: 127.0.0.1), `PORT` (default: 8050), `DEBUG` (default: false)

## Architecture

This is a Dash web application for real-time speech translation using Azure Cognitive Services.

### Data Flow

1. Browser captures audio via JavaScript (`assets/audio_recorder.js`) using MediaRecorder API
2. Audio is converted to WAV format and sent as base64 to Python backend
3. `azure_services.py` processes the audio:
   - Speech-to-Text transcription
   - Translation to two target languages via Azure Translator REST API
   - Text-to-Speech synthesis for all three texts
4. Base64-encoded audio responses are played sequentially in the browser

### Key Modules

- **app.py**: Dash application with UI layout and callbacks. Uses clientside callbacks for audio recording/playback (browser-side) and server callbacks for Azure processing.
- **azure_services.py**: Wraps Azure Speech SDK and Translator API. Main entry point is `process_recording()` which orchestrates STT → Translation → TTS.
- **languages.py**: Configuration mapping 15 language locales to Azure neural voices and translator codes.
- **rate_limiter.py**: IP-based rate limiting (10 recordings/day) with JSON file storage. Thread-safe.
- **assets/audio_recorder.js**: Browser-side audio capture. Exposes `window.dashAudioRecorder` for Dash clientside callbacks.

### Dash Callback Pattern

The app uses a hybrid callback approach:
- **Clientside callbacks** (JavaScript): Handle recording start/stop, timer updates, button styling, and audio playback
- **Server callbacks** (Python): Process audio through Azure services, update results display, check rate limits

State flows through `dcc.Store` components: `recording-state` → `audio-data-store` → `processing-result`
