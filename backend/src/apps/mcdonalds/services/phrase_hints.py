import json
from pathlib import Path

_LOCALE_TO_NAME_FIELD = {
    "en-US": "name",
    "en": "name",
    "de-DE": "name_de",
    "de": "name_de",
    "cs-CZ": "name_cs",
    "cs": "name_cs",
}

_menu_phrases: dict[str, list[str]] = {}


def _load_menu_phrases() -> dict[str, list[str]]:
    """Load menu item names per language from menu_items.json (cached)."""
    if _menu_phrases:
        return _menu_phrases
    menu_path = Path(__file__).resolve().parents[4] / "data" / "menu_items.json"
    items = json.loads(menu_path.read_text(encoding="utf-8"))
    for locale, field in _LOCALE_TO_NAME_FIELD.items():
        _menu_phrases[locale] = list({item[field] for item in items})
    return _menu_phrases


def get_menu_phrases(language: str) -> list[str]:
    """Return menu item name phrases for the given language/locale code."""
    phrases = _load_menu_phrases()
    return phrases.get(language, phrases.get("en-US", []))
