# Transport Voice Translation

Speech-to-speech translation app. Record audio in one language and get text translations plus synthesized audio in two target languages.

## How It Works

1. **Transcribe** — Decode base64 audio and transcribe with Azure Speech in the source language.
2. **Translate** — Translate the text into both target languages via Azure Translator.
3. **Synthesize** — Generate TTS audio for the original and both translations using Azure neural voices.

Supports 15 languages including English, Spanish, French, German, Italian, Portuguese, Chinese, Japanese, Korean, Russian, Arabic, Hindi, and Polish.

## API Routes

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/transport/process` | Transcribe + translate + TTS |
| GET | `/api/transport/languages` | List supported languages |

## Required Environment Variables

```
AZURE_SPEECH_KEY=...
AZURE_SPEECH_REGION=westeurope
AZURE_TRANSLATOR_KEY=...
```
