"""
Pydantic models for periodontal examination data.
Uses FDI/ISO tooth numbering system (11-48).
"""

from typing import Optional
from pydantic import BaseModel, Field


class SiteMeasurement(BaseModel):
    """Measurements for a single site on a tooth."""
    pd: Optional[int] = Field(None, ge=1, le=12, description="Probing depth in mm")
    cal: Optional[int] = Field(None, ge=0, le=15, description="Clinical attachment level in mm")
    recession: Optional[int] = Field(None, ge=0, le=10, description="Gingival recession in mm")
    bop: Optional[bool] = Field(None, description="Bleeding on probing")


class ToothData(BaseModel):
    """Data for a single tooth with 6 measurement sites."""
    tooth_number: int = Field(..., ge=11, le=48, description="FDI tooth number")
    sites: dict[str, SiteMeasurement] = Field(
        default_factory=lambda: {
            "mesio_buccal": SiteMeasurement(),
            "mid_buccal": SiteMeasurement(),
            "disto_buccal": SiteMeasurement(),
            "mesio_lingual": SiteMeasurement(),
            "mid_lingual": SiteMeasurement(),
            "disto_lingual": SiteMeasurement(),
        },
        description="Measurements for 6 sites"
    )
    mobility: Optional[int] = Field(None, ge=0, le=3, description="Tooth mobility grade")
    furcation: Optional[int] = Field(None, ge=0, le=3, description="Furcation involvement grade")
    plaque: Optional[bool] = Field(None, description="Plaque present")
    calculus: Optional[bool] = Field(None, description="Calculus present")


class PeriodontalExam(BaseModel):
    """Complete periodontal examination data."""
    teeth: dict[str, ToothData] = Field(default_factory=dict, description="Teeth data keyed by tooth number")
    raw_transcription: str = Field(..., description="Original transcribed text")
    extraction_notes: Optional[str] = Field(None, description="Notes about extraction ambiguities")


# FDI tooth numbering reference
# Upper jaw: 11-18 (right), 21-28 (left)
# Lower jaw: 31-38 (left), 41-48 (right)
VALID_TOOTH_NUMBERS = [
    # Upper right quadrant (1x)
    18, 17, 16, 15, 14, 13, 12, 11,
    # Upper left quadrant (2x)
    21, 22, 23, 24, 25, 26, 27, 28,
    # Lower left quadrant (3x)
    31, 32, 33, 34, 35, 36, 37, 38,
    # Lower right quadrant (4x)
    41, 42, 43, 44, 45, 46, 47, 48,
]

# Molars (can have furcation involvement)
MOLAR_TEETH = [16, 17, 18, 26, 27, 28, 36, 37, 38, 46, 47, 48]

# Site names for display
SITE_NAMES = {
    "mesio_buccal": "MB",
    "mid_buccal": "B",
    "disto_buccal": "DB",
    "mesio_lingual": "ML",
    "mid_lingual": "L",
    "disto_lingual": "DL",
}

# Buccal and lingual site groups
BUCCAL_SITES = ["mesio_buccal", "mid_buccal", "disto_buccal"]
LINGUAL_SITES = ["mesio_lingual", "mid_lingual", "disto_lingual"]


def get_max_pd(tooth: ToothData) -> Optional[int]:
    """Get the maximum probing depth for a tooth."""
    max_pd = None
    for site in tooth.sites.values():
        if site.pd is not None:
            if max_pd is None or site.pd > max_pd:
                max_pd = site.pd
    return max_pd


def get_severity_color(pd: Optional[int]) -> str:
    """Get color code based on probing depth severity."""
    if pd is None:
        return "#e0e0e0"  # Gray for no data
    elif pd <= 3:
        return "#4CAF50"  # Green - healthy
    elif pd == 4:
        return "#FFEB3B"  # Yellow - early inflammation
    elif pd <= 6:
        return "#FF9800"  # Orange - moderate
    else:
        return "#F44336"  # Red - severe


def has_bleeding(tooth: ToothData) -> bool:
    """Check if any site on the tooth has bleeding on probing."""
    return any(site.bop is True for site in tooth.sites.values())
