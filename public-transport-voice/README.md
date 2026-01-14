# Public Transport Voice

Multilingual announcements that everyone understands

Break language barriers in public transport. Record an announcement once and instantly deliver it in multiple languages with natural-sounding AI voices.

## The Problem

Every day, thousands of passengers miss critical announcements because they don't speak the local language. Delayed trains, platform changes, safety warnings - all lost in translation. This leads to confusion, missed connections, and frustrated travelers.

## The Solution

Public Transport Voice transforms any announcement into multiple languages instantly. Using advanced AI, it preserves the natural tone and urgency of the original message while making it accessible to everyone - no matter what language they speak.


## Quick Start

1. **Install dependencies**
   ```bash
   uv sync
   ```

2. **Configure Azure credentials**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your Azure Speech and Translator keys.

3. **Run the application**
   ```bash
   uv run app.py
   ```

4. **Open in browser**
   Navigate to `http://localhost:8050`

## Azure keys
   * Azure speech: https://azure.microsoft.com/en-us/products/ai-foundry/tools/speechAzure 
   * Azure translate: https://azure.microsoft.com/en-us/products/ai-foundry/tools/translator


