# Dictation for Dental Hygienists

A voice-powered Dash application for dental hygienists to dictate periodontal examination findings. The app transcribes speech, extracts structured data using AI, and displays results in a visual dental arch chart.

## Features

- **Multi-language support**: English, German, and Czech
- **Voice transcription**: Azure Speech-to-Text
- **AI data extraction**: Azure OpenAI (gpt-5-nano) extracts structured periodontal data
- **Visual dental chart**: SVG-based dental arch visualization with color-coded severity
- **FDI/ISO tooth numbering**: International standard (11-48)

## Extracted Data

The app extracts the following measurements for each tooth:
- **Probing Depth (PD)**: 1-12mm at 6 sites per tooth
- **Clinical Attachment Level (CAL)**: 0-15mm
- **Gingival Recession**: 0-10mm
- **Bleeding on Probing (BOP)**: yes/no
- **Mobility**: 0-3 scale
- **Furcation**: 0-3 scale (molars only)

## Setup

1. **Create environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Configure Azure credentials** in `.env`:
   - `AZURE_SPEECH_KEY`: Azure Speech Service key
   - `AZURE_SPEECH_REGION`: Azure Speech Service region
   - `AZURE_OPENAI_ENDPOINT`: Azure OpenAI endpoint URL
   - `AZURE_OPENAI_KEY`: Azure OpenAI key
   - `AZURE_OPENAI_DEPLOYMENT`: Model deployment name (gpt-5-nano)

3. **Install dependencies**:
   ```bash
   uv sync
   ```

4. **Run the application**:
   ```bash
   uv run app.py
   ```

5. Open http://localhost:8051 in your browser

## Usage

1. Select your language (English, German, or Czech)
2. Click "Start Recording" and dictate the periodontal findings
3. Click "Stop Recording" when finished
4. View the extracted data in the dental chart and detailed tables

## Example Dictation

**English:**
> "Tooth 16, probing depths 3-4-5 buccal, 3-3-4 lingual. Bleeding at mesio-buccal and disto-buccal. Furcation grade 2."

**German:**
> "Zahn 16, Sondierungstiefen bukkal 3-4-5, lingual 3-3-4. Blutung mesio-bukkal und disto-bukkal. Furkation Grad 2."

**Czech:**
> "Zub 16, hloubky sondáže 3-4-5 bukálně, 3-3-4 lingválně. Krvácení mesio-bukálně a disto-bukálně. Furkace stupeň 2."
