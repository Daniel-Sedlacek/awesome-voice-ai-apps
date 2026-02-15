# Dental Dictation & Periodontal Data Extraction

Dentists dictate periodontal exam notes; the system transcribes the audio and uses an LLM to extract structured clinical data.

## How It Works

1. **Transcribe** — Continuous transcription via Azure Speech (handles longer dictations).
2. **Extract** — Azure OpenAI parses the transcript into structured periodontal data using few-shot examples.
3. **Return** — Structured exam data with FDI tooth numbers (11-48), 6-site measurements per tooth, and tooth-level findings.

### Extracted Data Per Tooth

- **6 sites:** mesio-buccal, mid-buccal, disto-buccal, mesio-lingual, mid-lingual, disto-lingual
- **Per site:** probing depth (1-12mm), CAL (0-15mm), recession (0-10mm), BOP (true/false)
- **Per tooth:** mobility (0-3), furcation (0-3, molars only), plaque, calculus

Supports English, German, and Czech with locale-specific example dictations.

## API Routes

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/dental/process` | Transcribe + extract exam data |
| GET | `/api/dental/languages` | List supported languages |

## Required Environment Variables

```
AZURE_SPEECH_KEY=...
AZURE_SPEECH_REGION=westeurope
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_KEY=...
AZURE_OPENAI_DEPLOYMENT=gpt-4.1-mini
```
