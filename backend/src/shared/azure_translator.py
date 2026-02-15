"""
Azure Translator service wrapper.
"""

import uuid

import requests as http_requests

from src.settings import get_settings
from src.shared.azure_stt import AzureServiceError
from src.settings import get_settings


settings = get_settings()


def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """
    Translate text using Azure Translator.

    Args:
        text: Text to translate
        source_lang: Source language code (e.g., "en")
        target_lang: Target language code (e.g., "es")

    Returns:
        Translated text

    Raises:
        AzureServiceError: If translation fails
    """
    settings = get_settings()
    if not settings.AZURE_TRANSLATOR_KEY:
        raise AzureServiceError("Azure Translator Key not configured")

    if not text.strip():
        return ""

    if source_lang == target_lang:
        return text

    try:
        url = f"{settings.TRANSLATOR_ENDPOINT}/translate"
        params = {
            "api-version": "3.0",
            "from": source_lang,
            "to": target_lang,
        }
        headers = {
            "Ocp-Apim-Subscription-Key": settings.AZURE_TRANSLATOR_KEY,
            "Ocp-Apim-Subscription-Region": settings.AZURE_TRANSLATOR_REGION,
            "Content-Type": "application/json",
            "X-ClientTraceId": str(uuid.uuid4()),
        }
        body = [{"text": text}]

        response = http_requests.post(url, params=params, headers=headers, json=body, timeout=30)
        response.raise_for_status()

        result = response.json()
        if result and len(result) > 0 and "translations" in result[0]:
            return result[0]["translations"][0]["text"]
        else:
            raise AzureServiceError("Unexpected translation response format")

    except http_requests.exceptions.RequestException as e:
        raise AzureServiceError(f"Translation request failed: {str(e)}")
    except (KeyError, IndexError) as e:
        raise AzureServiceError(f"Failed to parse translation response: {str(e)}")
