"""
Azure OpenAI service for extracting periodontal data from transcribed text.
Uses gpt-5-nano with few-shot examples for structured extraction.
"""

import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv

from data_models import PeriodontalExam, ToothData, SiteMeasurement

# Load environment variables
load_dotenv()

# Azure OpenAI configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY", "")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5-nano")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2025-08-07")


class ExtractionError(Exception):
    """Custom exception for extraction errors."""
    pass


# System prompt with rules and few-shot examples
SYSTEM_PROMPT = """You are a dental data extraction assistant. Extract periodontal examination data from dictated notes. Output valid JSON matching the schema below.

## Rules
1. Tooth numbers use FDI/ISO notation (11-48)
2. Six sites per tooth: mesio_buccal (MB), mid_buccal (B), disto_buccal (DB), mesio_lingual (ML), mid_lingual (L), disto_lingual (DL)
3. Probing depth (PD): integers 1-12 mm
4. Clinical attachment level (CAL): integers 0-15 mm
5. Recession: integers 0-10 mm
6. Bleeding on probing (BOP): true/false
7. Mobility: integers 0-3
8. Furcation: integers 0-3 (only for molars: 16-18, 26-28, 36-38, 46-48)
9. If information is ambiguous or missing, set those fields to null
10. Add any warnings or clarifications to extraction_notes

## JSON Schema
{
  "teeth": {
    "<tooth_number>": {
      "tooth_number": <int>,
      "sites": {
        "mesio_buccal": {"pd": <int|null>, "cal": <int|null>, "recession": <int|null>, "bop": <bool|null>},
        "mid_buccal": {"pd": <int|null>, "cal": <int|null>, "recession": <int|null>, "bop": <bool|null>},
        "disto_buccal": {"pd": <int|null>, "cal": <int|null>, "recession": <int|null>, "bop": <bool|null>},
        "mesio_lingual": {"pd": <int|null>, "cal": <int|null>, "recession": <int|null>, "bop": <bool|null>},
        "mid_lingual": {"pd": <int|null>, "cal": <int|null>, "recession": <int|null>, "bop": <bool|null>},
        "disto_lingual": {"pd": <int|null>, "cal": <int|null>, "recession": <int|null>, "bop": <bool|null|}
      },
      "mobility": <int|null>,
      "furcation": <int|null>,
      "plaque": <bool|null>,
      "calculus": <bool|null>
    }
  },
  "raw_transcription": "<original text>",
  "extraction_notes": "<string|null>"
}

## Few-Shot Examples

### Example 1 (English)
**Input:**
"Tooth 11, probing depths 2-2-3 buccal, 2-2-2 lingual. Bleeding at disto-buccal."

**Output:**
{"teeth": {"11": {"tooth_number": 11, "sites": {"mesio_buccal": {"pd": 2, "cal": null, "recession": null, "bop": false}, "mid_buccal": {"pd": 2, "cal": null, "recession": null, "bop": false}, "disto_buccal": {"pd": 3, "cal": null, "recession": null, "bop": true}, "mesio_lingual": {"pd": 2, "cal": null, "recession": null, "bop": false}, "mid_lingual": {"pd": 2, "cal": null, "recession": null, "bop": false}, "disto_lingual": {"pd": 2, "cal": null, "recession": null, "bop": false}}, "mobility": null, "furcation": null, "plaque": null, "calculus": null}}, "raw_transcription": "Tooth 11, probing depths 2-2-3 buccal, 2-2-2 lingual. Bleeding at disto-buccal.", "extraction_notes": null}

### Example 2 (German)
**Input:**
"Zahn 16, Sondierungstiefen bukkal 3-4-5, lingual 3-3-4. Furkation Grad 2. Blutung mesio-bukkal und disto-bukkal."

**Output:**
{"teeth": {"16": {"tooth_number": 16, "sites": {"mesio_buccal": {"pd": 3, "cal": null, "recession": null, "bop": true}, "mid_buccal": {"pd": 4, "cal": null, "recession": null, "bop": false}, "disto_buccal": {"pd": 5, "cal": null, "recession": null, "bop": true}, "mesio_lingual": {"pd": 3, "cal": null, "recession": null, "bop": false}, "mid_lingual": {"pd": 3, "cal": null, "recession": null, "bop": false}, "disto_lingual": {"pd": 4, "cal": null, "recession": null, "bop": false}}, "mobility": null, "furcation": 2, "plaque": null, "calculus": null}}, "raw_transcription": "Zahn 16, Sondierungstiefen bukkal 3-4-5, lingual 3-3-4. Furkation Grad 2. Blutung mesio-bukkal und disto-bukkal.", "extraction_notes": null}

### Example 3 (Czech)
**Input:**
"Zub 36, hloubky sondáže 4-5-6 bukálně, 3-4-4 lingválně. Recese 2mm vestibulárně. Pohyblivost stupeň 1."

**Output:**
{"teeth": {"36": {"tooth_number": 36, "sites": {"mesio_buccal": {"pd": 4, "cal": null, "recession": 2, "bop": null}, "mid_buccal": {"pd": 5, "cal": null, "recession": 2, "bop": null}, "disto_buccal": {"pd": 6, "cal": null, "recession": 2, "bop": null}, "mesio_lingual": {"pd": 3, "cal": null, "recession": null, "bop": null}, "mid_lingual": {"pd": 4, "cal": null, "recession": null, "bop": null}, "disto_lingual": {"pd": 4, "cal": null, "recession": null, "bop": null}}, "mobility": 1, "furcation": null, "plaque": null, "calculus": null}}, "raw_transcription": "Zub 36, hloubky sondáže 4-5-6 bukálně, 3-4-4 lingválně. Recese 2mm vestibulárně. Pohyblivost stupeň 1.", "extraction_notes": "Recession applied to all buccal sites as 'vestibulárně' indicates buccal surface."}

### Example 4 (English - Multiple teeth)
**Input:**
"Upper right quadrant. Tooth 17, depths 3-3-3-3-3-3, no bleeding. Tooth 16, depths 4-5-5-3-3-4, bleeding mesial and distal. Mobility grade 1."

**Output:**
{"teeth": {"17": {"tooth_number": 17, "sites": {"mesio_buccal": {"pd": 3, "cal": null, "recession": null, "bop": false}, "mid_buccal": {"pd": 3, "cal": null, "recession": null, "bop": false}, "disto_buccal": {"pd": 3, "cal": null, "recession": null, "bop": false}, "mesio_lingual": {"pd": 3, "cal": null, "recession": null, "bop": false}, "mid_lingual": {"pd": 3, "cal": null, "recession": null, "bop": false}, "disto_lingual": {"pd": 3, "cal": null, "recession": null, "bop": false}}, "mobility": null, "furcation": null, "plaque": null, "calculus": null}, "16": {"tooth_number": 16, "sites": {"mesio_buccal": {"pd": 4, "cal": null, "recession": null, "bop": true}, "mid_buccal": {"pd": 5, "cal": null, "recession": null, "bop": false}, "disto_buccal": {"pd": 5, "cal": null, "recession": null, "bop": true}, "mesio_lingual": {"pd": 3, "cal": null, "recession": null, "bop": true}, "mid_lingual": {"pd": 3, "cal": null, "recession": null, "bop": false}, "disto_lingual": {"pd": 4, "cal": null, "recession": null, "bop": true}}, "mobility": 1, "furcation": null, "plaque": null, "calculus": null}}, "raw_transcription": "Upper right quadrant. Tooth 17, depths 3-3-3-3-3-3, no bleeding. Tooth 16, depths 4-5-5-3-3-4, bleeding mesial and distal. Mobility grade 1.", "extraction_notes": "Bleeding 'mesial and distal' interpreted as mesio-buccal, disto-buccal, mesio-lingual, disto-lingual sites."}

Now extract data from the following transcription. Return ONLY valid JSON, no additional text."""


def get_openai_client() -> AzureOpenAI:
    """Create and return Azure OpenAI client."""
    if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_KEY:
        raise ExtractionError("Azure OpenAI credentials not configured")

    return AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
    )


def extract_periodontal_data(transcription: str) -> PeriodontalExam:
    """
    Extract structured periodontal data from transcribed text using Azure OpenAI.

    Args:
        transcription: The transcribed text from speech recognition

    Returns:
        PeriodontalExam object with structured data

    Raises:
        ExtractionError: If extraction fails
    """
    if not transcription.strip():
        raise ExtractionError("No transcription provided")

    try:
        client = get_openai_client()

        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": transcription},
            ],
            temperature=0.1,  # Low temperature for consistent extraction
            max_tokens=4000,
            response_format={"type": "json_object"},
        )

        result_text = response.choices[0].message.content
        if not result_text:
            raise ExtractionError("Empty response from LLM")

        # Parse JSON response
        result_data = json.loads(result_text)

        # Ensure raw_transcription is set
        result_data["raw_transcription"] = transcription

        # Convert to Pydantic model
        exam = parse_extraction_result(result_data)
        return exam

    except json.JSONDecodeError as e:
        raise ExtractionError(f"Failed to parse LLM response as JSON: {str(e)}")
    except Exception as e:
        raise ExtractionError(f"Extraction failed: {str(e)}")


def parse_extraction_result(data: dict) -> PeriodontalExam:
    """
    Parse the LLM extraction result into a PeriodontalExam object.

    Args:
        data: Dictionary from LLM JSON response

    Returns:
        PeriodontalExam object
    """
    teeth_data = {}

    for tooth_key, tooth_value in data.get("teeth", {}).items():
        # Parse sites
        sites = {}
        for site_name, site_data in tooth_value.get("sites", {}).items():
            sites[site_name] = SiteMeasurement(
                pd=site_data.get("pd"),
                cal=site_data.get("cal"),
                recession=site_data.get("recession"),
                bop=site_data.get("bop"),
            )

        # Fill in missing sites with empty measurements
        for site_name in ["mesio_buccal", "mid_buccal", "disto_buccal",
                          "mesio_lingual", "mid_lingual", "disto_lingual"]:
            if site_name not in sites:
                sites[site_name] = SiteMeasurement()

        teeth_data[tooth_key] = ToothData(
            tooth_number=tooth_value.get("tooth_number", int(tooth_key)),
            sites=sites,
            mobility=tooth_value.get("mobility"),
            furcation=tooth_value.get("furcation"),
            plaque=tooth_value.get("plaque"),
            calculus=tooth_value.get("calculus"),
        )

    return PeriodontalExam(
        teeth=teeth_data,
        raw_transcription=data.get("raw_transcription", ""),
        extraction_notes=data.get("extraction_notes"),
    )


def exam_to_dict(exam: PeriodontalExam) -> dict:
    """Convert PeriodontalExam to a serializable dictionary."""
    return exam.model_dump()
