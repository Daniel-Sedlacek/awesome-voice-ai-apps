"""
Dental terminology phrase hints for Azure Speech-to-Text.
Biases recognition toward domain-specific dental/periodontal terms.
"""

_PHRASES: dict[str, list[str]] = {
    "en": [
        "buccal", "lingual", "mesial", "distal",
        "mesio-buccal", "mid-buccal", "disto-buccal",
        "mesio-lingual", "mid-lingual", "disto-lingual",
        "probing depth", "pocket depth", "recession",
        "bleeding on probing", "mobility", "furcation",
        "calculus", "plaque", "clinical attachment level",
        "gingival", "periodontal", "millimeters",
        *[f"tooth {n}" for n in range(11, 49) if n % 10 != 0 and n % 10 <= 8],
    ],
    "de": [
        "bukkal", "lingual", "mesial", "distal",
        "mesio-bukkal", "disto-bukkal",
        "Sondierungstiefe", "Taschentiefe", "Rezession",
        "Blutung bei Sondierung", "Beweglichkeit", "Furkation",
        "Zahnstein", "Plaque", "klinisches Attachmentlevel",
        "gingival", "parodontal", "Millimeter",
        *[f"Zahn {n}" for n in range(11, 49) if n % 10 != 0 and n % 10 <= 8],
    ],
    "cs": [
        "bukální", "lingvální", "mesiální", "distální",
        "hloubka kapsy", "hloubka sondáže", "recese",
        "krvácení při sondáži", "pohyblivost", "furkace",
        "zubní kámen", "plak", "klinická ztráta přilnavosti",
        "gingivální", "parodontální", "milimetry",
        *[f"zub {n}" for n in range(11, 49) if n % 10 != 0 and n % 10 <= 8],
    ],
}


def get_dental_phrases(locale: str) -> list[str]:
    """Return dental terminology phrases for the given locale code."""
    lang = locale.split("-")[0]
    return _PHRASES.get(lang, _PHRASES["en"])
