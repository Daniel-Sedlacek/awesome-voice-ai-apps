"""
Msgspec models for periodontal examination data.
Uses FDI/ISO tooth numbering system (11-48).
"""

from typing import Annotated

import msgspec
from msgspec import Meta, Struct


class SiteMeasurement(Struct):
    """Measurements for a single site on a tooth."""
    pd: Annotated[int, Meta(ge=1, le=12, description="Probing depth in mm")] | None = None
    cal: Annotated[int, Meta(ge=0, le=15, description="Clinical attachment level in mm")] | None = None
    recession: Annotated[int, Meta(ge=0, le=10, description="Gingival recession in mm")] | None = None
    bop: Annotated[bool, Meta(description="Bleeding on probing")] | None = None


class ToothData(Struct):
    """Data for a single tooth with 6 measurement sites."""
    tooth_number: Annotated[int, Meta(ge=11, le=48, description="FDI tooth number")]
    sites: Annotated[dict[str, SiteMeasurement], Meta(description="Measurements for 6 sites")] = msgspec.field(
        default_factory=lambda: {
            "mesio_buccal": SiteMeasurement(),
            "mid_buccal": SiteMeasurement(),
            "disto_buccal": SiteMeasurement(),
            "mesio_lingual": SiteMeasurement(),
            "mid_lingual": SiteMeasurement(),
            "disto_lingual": SiteMeasurement(),
        }
    )
    mobility: Annotated[int, Meta(ge=0, le=3, description="Tooth mobility grade")] | None = None
    furcation: Annotated[int, Meta(ge=0, le=3, description="Furcation involvement grade")] | None = None
    plaque: Annotated[bool, Meta(description="Plaque present")] | None = None
    calculus: Annotated[bool, Meta(description="Calculus present")] | None = None


class PeriodontalExam(Struct):
    """Complete periodontal examination data."""
    raw_transcription: Annotated[str, Meta(description="Original transcribed text")]
    teeth: Annotated[dict[str, ToothData], Meta(description="Teeth data keyed by tooth number")] = msgspec.field(default_factory=dict)
    extraction_notes: Annotated[str, Meta(description="Notes about extraction ambiguities")] | None = None


VALID_TOOTH_NUMBERS = [
    18, 17, 16, 15, 14, 13, 12, 11,
    21, 22, 23, 24, 25, 26, 27, 28,
    31, 32, 33, 34, 35, 36, 37, 38,
    41, 42, 43, 44, 45, 46, 47, 48,
]

MOLAR_TEETH = [16, 17, 18, 26, 27, 28, 36, 37, 38, 46, 47, 48]

SITE_NAMES = {
    "mesio_buccal": "MB",
    "mid_buccal": "B",
    "disto_buccal": "DB",
    "mesio_lingual": "ML",
    "mid_lingual": "L",
    "disto_lingual": "DL",
}

BUCCAL_SITES = ["mesio_buccal", "mid_buccal", "disto_buccal"]
LINGUAL_SITES = ["mesio_lingual", "mid_lingual", "disto_lingual"]


def get_max_pd(tooth: ToothData) -> int | None:
    """Get the maximum probing depth for a tooth."""
    max_pd = None
    for site in tooth.sites.values():
        if site.pd is not None:
            if max_pd is None or site.pd > max_pd:
                max_pd = site.pd
    return max_pd


def get_severity_color(pd: int | None) -> str:
    """Get color code based on probing depth severity."""
    if pd is None:
        return "#e0e0e0"
    elif pd <= 3:
        return "#4CAF50"
    elif pd == 4:
        return "#FFEB3B"
    elif pd <= 6:
        return "#FF9800"
    else:
        return "#F44336"


def has_bleeding(tooth: ToothData) -> bool:
    """Check if any site on the tooth has bleeding on probing."""
    return any(site.bop is True for site in tooth.sites.values())
