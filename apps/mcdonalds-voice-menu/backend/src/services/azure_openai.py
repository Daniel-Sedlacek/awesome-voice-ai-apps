import json
from openai import OpenAI
from src.config import get_settings


def get_openai_client() -> OpenAI:
    """Get Azure OpenAI client (OpenAI-compatible endpoint)"""
    settings = get_settings()
    base_url = settings.AZURE_OPENAI_ENDPOINT.rstrip("/")
    if not base_url.endswith("/openai/v1"):
        base_url = f"{base_url}/openai/v1"
    return OpenAI(
        api_key=settings.AZURE_OPENAI_KEY,
        base_url=base_url,
    )


# Intent classification prompt
INTENT_SYSTEM_PROMPT = """You are a McDonald's voice ordering assistant.
Analyze the user's speech and determine their intent.

## Intents
- ADD: User wants to search for or see menu items matching criteria (browsing)
- REMOVE: User wants to remove items from their search results view
- SELECT: User wants to add a specific displayed item to their order/basket
- REMOVE_FROM_BASKET: User wants to remove an item from their order/basket
- CLEAR: User wants to start over / clear everything
- CONFIRM: User is happy with their order

## Output JSON
{
  "intent": "ADD" | "REMOVE" | "SELECT" | "REMOVE_FROM_BASKET" | "CLEAR" | "CONFIRM",
  "search_criteria": "extracted food criteria for search (only for ADD)",
  "new_search": true/false (only for ADD - true if this is a new topic, false if refining the previous search),
  "remove_items": ["item names to remove from search results (only for REMOVE)"],
  "select_items": ["item names to add to basket (only for SELECT)"],
  "basket_remove_items": ["item names to remove from basket (only for REMOVE_FROM_BASKET)"]
}

## Key Distinction
- ADD vs SELECT: ADD means the user is searching/browsing ("show me burgers", "I want something spicy"). SELECT means the user has decided on a specific item from what they see ("I'll take the Big Mac", "add the McFlurry to my order", "yes, the cheeseburger please").
- REMOVE vs REMOVE_FROM_BASKET: REMOVE removes from search results ("don't show me the salad"). REMOVE_FROM_BASKET removes from the user's order ("remove the Big Mac from my order", "take the fries off my order").
- new_search (for ADD only): Set to true when the user is asking about a completely different category or topic (e.g. switching from burgers to drinks). Set to false when the user is refining or narrowing their current search (e.g. "with cheese" after asking for burgers). When in doubt, set to true.

## Examples
User: "I want a burger" → {"intent": "ADD", "search_criteria": "burger", "new_search": true}
User: "With two patties" → {"intent": "ADD", "search_criteria": "two patties burger", "new_search": false}
User: "Show me something to drink" → {"intent": "ADD", "search_criteria": "drinks beverages", "new_search": true}
User: "Something cold" (after drinks) → {"intent": "ADD", "search_criteria": "cold drinks", "new_search": false}
User: "Show me something healthy" → {"intent": "ADD", "search_criteria": "healthy low calorie", "new_search": true}
User: "Actually remove the Big Mac" → {"intent": "REMOVE", "remove_items": ["Big Mac"]}
User: "I'll take the Big Mac" → {"intent": "SELECT", "select_items": ["Big Mac"]}
User: "Add the McFlurry and the fries to my order" → {"intent": "SELECT", "select_items": ["McFlurry", "French Fries"]}
User: "Yes, the cheeseburger please" → {"intent": "SELECT", "select_items": ["Cheeseburger"]}
User: "I would buy a cheeseburger" → {"intent": "SELECT", "select_items": ["Cheeseburger"]}
User: "Remove the Big Mac from my order" → {"intent": "REMOVE_FROM_BASKET", "basket_remove_items": ["Big Mac"]}
User: "I don't want the fries anymore" → {"intent": "REMOVE_FROM_BASKET", "basket_remove_items": ["French Fries"]}
User: "Take the McChicken off my order" → {"intent": "REMOVE_FROM_BASKET", "basket_remove_items": ["McChicken"]}
User: "Start over" → {"intent": "CLEAR"}
User: "That looks good, I'm done" → {"intent": "CONFIRM"}
"""


async def parse_intent(transcript: str, conversation_history: list[dict]) -> dict:
    """Parse user intent from transcript using Azure OpenAI"""
    settings = get_settings()
    client = get_openai_client()

    messages = [{'role': 'system', 'content': INTENT_SYSTEM_PROMPT}]

    # Add conversation history for context
    for entry in conversation_history:
        messages.append({"role": "user", "content": entry["text"]})
    
    messages.append({"role": "user", "content": transcript})

    response = client.chat.completions.create(
        model=settings.AZURE_OPENAI_DEPLOYMENT,
        messages=messages,
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)