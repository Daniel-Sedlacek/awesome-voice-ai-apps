"""
Dental arch chart visualization using SVG.
Displays periodontal examination data in a visual format.
"""

from dash import html
from data_models import (
    PeriodontalExam, ToothData, VALID_TOOTH_NUMBERS,
    get_max_pd, get_severity_color, has_bleeding, SITE_NAMES
)


# Tooth positions for SVG rendering
# Format: (x, y) coordinates for each tooth
TOOTH_POSITIONS = {
    # Upper arch (displayed at top)
    # Right side (18-11) - from patient's perspective
    18: (50, 60), 17: (90, 50), 16: (130, 45), 15: (170, 42),
    14: (210, 40), 13: (250, 40), 12: (290, 42), 11: (330, 45),
    # Left side (21-28)
    21: (370, 45), 22: (410, 42), 23: (450, 40), 24: (490, 40),
    25: (530, 42), 26: (570, 45), 27: (610, 50), 28: (650, 60),

    # Lower arch (displayed at bottom)
    # Left side (31-38)
    38: (650, 240), 37: (610, 250), 36: (570, 255), 35: (530, 258),
    34: (490, 260), 33: (450, 260), 32: (410, 258), 31: (370, 255),
    # Right side (41-48)
    41: (330, 255), 42: (290, 258), 43: (250, 260), 44: (210, 260),
    45: (170, 258), 46: (130, 255), 47: (90, 250), 48: (50, 240),
}

TOOTH_RADIUS = 18


def create_tooth_svg(
    tooth_num: int,
    x: int,
    y: int,
    tooth_data: ToothData | None = None
) -> str:
    """Create SVG elements for a single tooth."""
    # Determine fill color based on max PD
    if tooth_data:
        max_pd = get_max_pd(tooth_data)
        fill_color = get_severity_color(max_pd)
        has_bop = has_bleeding(tooth_data)
    else:
        fill_color = "#e0e0e0"
        has_bop = False

    # Main tooth circle
    tooth_svg = f'''
        <g class="tooth" data-tooth="{tooth_num}">
            <circle cx="{x}" cy="{y}" r="{TOOTH_RADIUS}"
                    fill="{fill_color}" stroke="#333" stroke-width="2"
                    class="tooth-circle"/>
            <text x="{x}" y="{y + 5}" text-anchor="middle"
                  font-size="12" font-weight="bold" fill="#333">{tooth_num}</text>
    '''

    # Add bleeding indicator (red dot)
    if has_bop:
        tooth_svg += f'''
            <circle cx="{x + 12}" cy="{y - 12}" r="5"
                    fill="#F44336" stroke="#fff" stroke-width="1"/>
        '''

    tooth_svg += '</g>'
    return tooth_svg


def create_dental_chart_svg(exam: PeriodontalExam | None = None) -> str:
    """
    Create complete dental arch SVG visualization.

    Args:
        exam: PeriodontalExam data or None for empty chart

    Returns:
        SVG string for the dental chart
    """
    svg_content = '''
    <svg viewBox="0 0 700 320" xmlns="http://www.w3.org/2000/svg" class="dental-chart">
        <!-- Background -->
        <rect width="700" height="320" fill="#fafafa"/>

        <!-- Upper arch label -->
        <text x="350" y="25" text-anchor="middle" font-size="14" fill="#666">Upper Arch</text>

        <!-- Upper arch outline -->
        <path d="M 30,80 Q 350,0 670,80" fill="none" stroke="#ddd" stroke-width="2"/>

        <!-- Lower arch label -->
        <text x="350" y="295" text-anchor="middle" font-size="14" fill="#666">Lower Arch</text>

        <!-- Lower arch outline -->
        <path d="M 30,220 Q 350,300 670,220" fill="none" stroke="#ddd" stroke-width="2"/>

        <!-- Legend -->
        <g transform="translate(20, 130)">
            <text x="0" y="0" font-size="10" fill="#666">Probing Depth:</text>
            <rect x="0" y="8" width="12" height="12" fill="#4CAF50"/>
            <text x="16" y="18" font-size="9" fill="#666">1-3mm</text>
            <rect x="50" y="8" width="12" height="12" fill="#FFEB3B"/>
            <text x="66" y="18" font-size="9" fill="#666">4mm</text>
            <rect x="95" y="8" width="12" height="12" fill="#FF9800"/>
            <text x="111" y="18" font-size="9" fill="#666">5-6mm</text>
            <rect x="145" y="8" width="12" height="12" fill="#F44336"/>
            <text x="161" y="18" font-size="9" fill="#666">7+mm</text>
            <circle cx="205" cy="14" r="5" fill="#F44336"/>
            <text x="215" y="18" font-size="9" fill="#666">Bleeding</text>
        </g>
    '''

    # Add teeth
    for tooth_num in VALID_TOOTH_NUMBERS:
        x, y = TOOTH_POSITIONS[tooth_num]
        tooth_data = None
        if exam and str(tooth_num) in exam.teeth:
            tooth_data = exam.teeth[str(tooth_num)]
        svg_content += create_tooth_svg(tooth_num, x, y, tooth_data)

    svg_content += '</svg>'
    return svg_content


def create_dental_chart_component(exam: PeriodontalExam | None = None) -> html.Div:
    """
    Create a Dash component containing the dental chart.

    Args:
        exam: PeriodontalExam data or None for empty chart

    Returns:
        Dash html.Div component with the chart
    """
    svg_string = create_dental_chart_svg(exam)

    # Wrap SVG in minimal HTML for iframe rendering
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; padding: 0; display: flex; justify-content: center; }}
            svg {{ max-width: 100%; height: auto; }}
        </style>
    </head>
    <body>{svg_string}</body>
    </html>
    '''

    return html.Div(
        [
            html.Iframe(
                srcDoc=html_content,
                className="dental-chart-container",
                style={
                    "width": "100%",
                    "height": "350px",
                    "border": "none",
                    "overflow": "hidden"
                }
            )
        ],
        className="chart-wrapper"
    )


def create_tooth_detail_table(tooth_data: ToothData) -> html.Table:
    """
    Create a detailed table for a single tooth's measurements.

    Args:
        tooth_data: ToothData object

    Returns:
        Dash html.Table component
    """
    rows = []

    # Header row
    header = html.Tr([
        html.Th("Site"),
        html.Th("PD"),
        html.Th("CAL"),
        html.Th("Rec"),
        html.Th("BOP"),
    ])
    rows.append(header)

    # Site rows
    for site_key, site_name in SITE_NAMES.items():
        site = tooth_data.sites.get(site_key)
        if site:
            bop_indicator = "+" if site.bop else ("-" if site.bop is False else "")
            row = html.Tr([
                html.Td(site_name),
                html.Td(str(site.pd) if site.pd is not None else "-"),
                html.Td(str(site.cal) if site.cal is not None else "-"),
                html.Td(str(site.recession) if site.recession is not None else "-"),
                html.Td(bop_indicator, className="bop-positive" if site.bop else ""),
            ])
            rows.append(row)

    # Additional info row
    extras = []
    if tooth_data.mobility is not None:
        extras.append(f"Mobility: {tooth_data.mobility}")
    if tooth_data.furcation is not None:
        extras.append(f"Furcation: {tooth_data.furcation}")
    if tooth_data.plaque:
        extras.append("Plaque")
    if tooth_data.calculus:
        extras.append("Calculus")

    if extras:
        rows.append(html.Tr([
            html.Td(", ".join(extras), colSpan=5, className="extras-row")
        ]))

    return html.Table(rows, className="tooth-detail-table")


def create_results_summary(exam: PeriodontalExam) -> html.Div:
    """
    Create a summary view of all extracted teeth data.

    Args:
        exam: PeriodontalExam object

    Returns:
        Dash html.Div component with summary
    """
    if not exam.teeth:
        return html.Div("No teeth data extracted.", className="no-data-message")

    tooth_cards = []
    for tooth_num in sorted(exam.teeth.keys(), key=lambda x: int(x)):
        tooth_data = exam.teeth[tooth_num]
        max_pd = get_max_pd(tooth_data)
        color = get_severity_color(max_pd)

        card = html.Div(
            [
                html.Div(
                    f"Tooth {tooth_num}",
                    className="tooth-card-header",
                    style={"backgroundColor": color}
                ),
                create_tooth_detail_table(tooth_data),
            ],
            className="tooth-card"
        )
        tooth_cards.append(card)

    return html.Div(
        [
            html.H3("Extracted Data"),
            html.Div(tooth_cards, className="tooth-cards-grid"),
            html.Div(
                [
                    html.H4("Transcription"),
                    html.P(exam.raw_transcription, className="transcription-text"),
                ],
                className="transcription-section"
            ),
            html.Div(
                [
                    html.H4("Notes"),
                    html.P(exam.extraction_notes or "None", className="notes-text"),
                ],
                className="notes-section"
            ) if exam.extraction_notes else None,
        ],
        className="results-summary"
    )
