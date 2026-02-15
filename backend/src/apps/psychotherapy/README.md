# Psychotherapy Session Tracker

Users record emotional wellness monologues; the system analyzes them and tracks psychological metrics over sessions.

## How It Works

1. **Transcribe** — Continuous transcription via Azure Speech.
2. **Analyze** — Azure OpenAI evaluates the monologue with a supportive (non-clinical) tone, scoring 6 metrics on a 1-10 scale.
3. **Store** — Sessions are stored in-memory, keyed by date. They reset on server restart.

### Tracked Metrics

- Anxiety, Depression, Stress
- Emotional Stability, Positive Affect, Energy Level

### Report Sections

Each analysis returns a structured report with: summary, key emotions, concerns/themes, and insights.

Supports English, German, and Czech with 5 pre-made monologues per language for demo purposes (high anxiety, low mood, work stress, positive/stable, mixed emotions).

## API Routes

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/psychotherapy/process` | Transcribe + analyze metrics |
| GET | `/api/psychotherapy/sessions` | Today's sessions |
| GET | `/api/psychotherapy/languages` | Languages + sample monologues |

## Required Environment Variables

```
AZURE_SPEECH_KEY=...
AZURE_SPEECH_REGION=westeurope
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_KEY=...
AZURE_OPENAI_DEPLOYMENT=gpt-4.1-mini
```
