import json
from openai import AzureOpenAI
from src.config import get_settings


def get_openai_client() -> AzureOpenAI:
    """Get Azure OpenAI client"""
    settings = get_settings()
    return AzureOpenAI(
        api_key=settings.AZURE_OPENAI_KEY,
        api_version="2024-08-01-preview",
        base_url=settings.AZURE_OPENAI_ENDPOINT
    )


# Intent classification prompt
INTENT_SYSTEM_PROMPT = """You are a McDonald's voice ordering assistant.
Analyze the user's speech and determine their intent.

## Intents
- ADD: User wants to see menu items matching criteria
- REMOVE: User wants to remove items from their view
- CLEAR: User wants to start over / clear everything
- CONFIRM: User is happy with selection

## Output JSON
{
  "intent": "ADD" | "REMOVE" | "CLEAR" | "CONFIRM",
  "search_criteria": "extracted food criteria for search (only for ADD)",
  "remove_items": ["item names to remove (only for REMOVE)"]
}

## Examples
User: "I want a burger" → {"intent": "ADD", "search_criteria": "burger"}
User: "Something with two patties" → {"intent": "ADD", "search_criteria": "two patties burger"}
User: "Show me something healthy" → {"intent": "ADD", "search_criteria": "healthy low calorie"}
User: "Actually remove the Big Mac" → {"intent": "REMOVE", "remove_items": ["Big Mac"]}
User: "Start over" → {"intent": "CLEAR"}
User: "That looks good" → {"intent": "CONFIRM"}
"""


async def parse_intent(transcript: str, conversation_history: list[dict]) -> dict:
    """Parse user intent from transcript using Azure OpenAI"""
    settings = get_settings()
    client = get_openai_client()

    messages = [{'role': 'system', 'content': INTENT_SYSTEM_PROMPT}]

    # Add conversation history for context
    for entry in conversation_history:
        messages.append({"role": "user", "content": transcript})

        response = client.chat.completions.create(
            model=settings.AZURE_OPENAI_DEPLOYMENT,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.1,
            verbosity="low"
        )

    return json.loads(response.choices[0].message.content)