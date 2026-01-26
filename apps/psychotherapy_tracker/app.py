"""
Psychotherapy Tracker - Voice-based psychological wellness tracker.

A Dash application that records voice monologues, transcribes them using
Azure Speech-to-Text, and analyzes psychological content using Azure OpenAI.
Displays results as radar charts and time series visualizations.
"""

import base64
from dash import Dash, html, dcc, callback, Output, Input, State, clientside_callback
import plotly.graph_objects as go

from languages import (
    get_language_options,
    get_monologue_options,
    get_monologue_text,
    get_translation,
)
from data_models import METRIC_NAMES, METRIC_COLORS
from azure_services import process_recording, AzureServiceError
import session_storage

# Initialize Dash app (same pattern as dictation app)
app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# Language options for dropdown
LANGUAGE_OPTIONS = [
    {"label": name, "value": locale}
    for locale, name in get_language_options()
]


def create_radar_chart(metrics: dict, locale: str = "en-US") -> go.Figure:
    """Create a radar chart for the psychological metrics."""
    metric_labels = METRIC_NAMES.get(locale, METRIC_NAMES["en-US"])

    categories = [metric_labels[k] for k in metrics.keys()]
    values = list(metrics.values())
    categories.append(categories[0])
    values.append(values[0])

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values,
            theta=categories,
            fill="toself",
            fillcolor="rgba(139, 92, 246, 0.3)",
            line=dict(color="rgba(139, 92, 246, 1)", width=2),
            marker=dict(size=8, color="rgba(139, 92, 246, 1)"),
        )
    )
    fig.update_layout(
        template="simple_white",
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10], tickvals=[2, 4, 6, 8, 10]),
        ),
        showlegend=False,
        margin=dict(l=60, r=60, t=40, b=40),
        height=350,
    )
    return fig


def create_time_series_chart(sessions: list[dict], locale: str = "en-US") -> go.Figure:
    """Create a time series chart showing metrics across sessions."""
    metric_labels = METRIC_NAMES.get(locale, METRIC_NAMES["en-US"])
    fig = go.Figure()

    if sessions:
        x_labels = [f"Session {i + 1}" for i in range(len(sessions))]
        for metric_key, color in METRIC_COLORS.items():
            y_values = [s.get("metrics", {}).get(metric_key, 0) for s in sessions]
            fig.add_trace(
                go.Scatter(
                    x=x_labels,
                    y=y_values,
                    mode="lines+markers",
                    name=metric_labels.get(metric_key, metric_key),
                    line=dict(color=color, width=2),
                    marker=dict(size=6),
                )
            )

    fig.update_layout(
        template="simple_white",
        yaxis=dict(range=[0, 10], tickvals=[0, 2, 4, 6, 8, 10]),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
        margin=dict(l=40, r=20, t=20, b=80),
        height=350,
    )
    return fig


# App layout (following dictation app structure)
app.layout = html.Div(
    [
        # Header
        html.Div(
            [
                html.H1("Psychotherapy Tracker"),
                html.P("Track your emotional wellness with voice"),
            ],
            className="app-header",
        ),
        # Control panel
        html.Div(
            [
                # Language selection
                html.Div(
                    [
                        html.Label("Language:"),
                        dcc.Dropdown(
                            id="language-selector",
                            options=LANGUAGE_OPTIONS,
                            value="en-US",
                            clearable=False,
                            style={"width": "200px"},
                        ),
                    ],
                    className="language-selector",
                ),
                # Monologue selection
                html.Div(
                    [
                        html.Label("Sample monologue:"),
                        dcc.Dropdown(
                            id="monologue-selector",
                            options=[
                                {"label": title, "value": mid}
                                for mid, title in get_monologue_options("en-US")
                            ],
                            value="high_anxiety",
                            clearable=False,
                            style={"width": "300px"},
                        ),
                    ],
                    className="monologue-selector",
                ),
                # Recording section
                html.Div(
                    [
                        html.Button(
                            "Start Recording",
                            id="record-button",
                            n_clicks=0,
                            className="record-button ready",
                        ),
                        html.Div(
                            id="timer-display",
                            children="0:30",
                            className="timer-display",
                        ),
                    ],
                    className="record-section",
                ),
                # Status display
                html.Div(
                    id="status-display",
                    children="Ready to record",
                    className="status-display ready",
                ),
            ],
            className="control-panel",
        ),
        # Sample text section
        html.Div(
            [
                html.H3("Sample text to read:"),
                html.P(
                    id="sample-text",
                    children=get_monologue_text("en-US", "high_anxiety"),
                    className="sample-text",
                ),
            ],
            className="sample-section",
        ),
        # Results section
        html.Div(
            id="results-container",
            className="results-section",
        ),
        # Hidden stores for state management
        dcc.Store(id="recording-state", data={"isRecording": False}),
        dcc.Store(id="audio-data-store", data=None),
        dcc.Store(id="session-result-store", data=None),
        dcc.Store(id="all-sessions-store", data=[]),
        dcc.Store(id="locale-store", data="en-US"),
        dcc.Interval(id="timer-interval", interval=1000, disabled=True),
    ],
    className="app-container",
)


# Clientside callback for handling recording start/stop (same pattern as dictation app)
clientside_callback(
    """
    async function(n_clicks, recordingState) {
        if (!n_clicks) {
            return [window.dash_clientside.no_update, window.dash_clientside.no_update,
                    window.dash_clientside.no_update, window.dash_clientside.no_update,
                    window.dash_clientside.no_update, window.dash_clientside.no_update];
        }

        const isRecording = recordingState?.isRecording || false;

        if (!isRecording) {
            // Start recording
            const result = await window.dashAudioRecorder.startRecording();
            if (result.success) {
                return [
                    {isRecording: true},
                    null,
                    false,  // Enable timer interval
                    "Recording...",
                    "status-display recording",
                    "record-button recording"
                ];
            } else {
                return [
                    {isRecording: false},
                    null,
                    true,
                    "Error: " + (result.error || "Could not access microphone"),
                    "status-display error",
                    "record-button ready"
                ];
            }
        } else {
            // Stop recording
            const result = await window.dashAudioRecorder.stopRecording();
            if (result.success) {
                return [
                    {isRecording: false},
                    result.audioData,
                    true,  // Disable timer interval
                    "Processing audio...",
                    "status-display processing",
                    "record-button ready"
                ];
            } else {
                return [
                    {isRecording: false},
                    null,
                    true,
                    "Error: " + (result.error || "Recording failed"),
                    "status-display error",
                    "record-button ready"
                ];
            }
        }
    }
    """,
    [
        Output("recording-state", "data"),
        Output("audio-data-store", "data"),
        Output("timer-interval", "disabled"),
        Output("status-display", "children"),
        Output("status-display", "className"),
        Output("record-button", "className"),
    ],
    Input("record-button", "n_clicks"),
    State("recording-state", "data"),
    prevent_initial_call=True,
)


# Clientside callback for updating timer display
clientside_callback(
    """
    function(n_intervals, recordingState) {
        if (!recordingState?.isRecording) {
            return "0:30";
        }
        const state = window.dashAudioRecorder.getRecordingState();
        const remaining = Math.ceil(state.remaining);
        return "0:" + (remaining < 10 ? "0" : "") + remaining;
    }
    """,
    Output("timer-display", "children"),
    Input("timer-interval", "n_intervals"),
    State("recording-state", "data"),
)


# Clientside callback for updating button text
clientside_callback(
    """
    function(recordingState) {
        const isRecording = recordingState?.isRecording || false;
        return isRecording ? "Stop Recording" : "Start Recording";
    }
    """,
    Output("record-button", "children"),
    Input("recording-state", "data"),
)


@callback(
    [
        Output("monologue-selector", "options"),
        Output("monologue-selector", "value"),
        Output("sample-text", "children"),
        Output("locale-store", "data"),
    ],
    Input("language-selector", "value"),
)
def update_language(locale: str):
    """Update UI when language changes."""
    options = [
        {"label": title, "value": mid}
        for mid, title in get_monologue_options(locale)
    ]
    first_mono = options[0]["value"] if options else None
    text = get_monologue_text(locale, first_mono) if first_mono else ""
    return options, first_mono, text, locale


@callback(
    Output("sample-text", "children", allow_duplicate=True),
    Input("monologue-selector", "value"),
    State("locale-store", "data"),
    prevent_initial_call=True,
)
def update_sample_text(mono_id: str, locale: str):
    """Update sample text when monologue selection changes."""
    if not mono_id:
        return ""
    return get_monologue_text(locale, mono_id)


@callback(
    [
        Output("session-result-store", "data"),
        Output("all-sessions-store", "data"),
        Output("status-display", "children", allow_duplicate=True),
        Output("status-display", "className", allow_duplicate=True),
    ],
    Input("audio-data-store", "data"),
    [State("locale-store", "data"), State("all-sessions-store", "data")],
    prevent_initial_call=True,
)
def process_audio(audio_data: str | None, locale: str, sessions: list):
    """Process recorded audio: transcribe and analyze."""
    if not audio_data:
        return None, sessions or [], "Ready to record", "status-display ready"

    sessions = sessions or []

    try:
        # Decode base64 audio data
        audio_bytes = base64.b64decode(audio_data)

        # Get session number
        session_number = len(sessions) + 1

        # Process through Azure services
        result = process_recording(audio_bytes, locale, session_number)

        # Convert to dict for storage
        result_dict = result.model_dump(mode="json")

        # Store session
        session_storage.store_session(result_dict)
        sessions.append(result_dict)

        return (
            result_dict,
            sessions,
            "Analysis complete!",
            "status-display success",
        )

    except AzureServiceError as e:
        return None, sessions, f"Error: {str(e)}", "status-display error"
    except Exception as e:
        return None, sessions, f"Error: {str(e)}", "status-display error"


@callback(
    Output("results-container", "children"),
    [Input("session-result-store", "data"), Input("all-sessions-store", "data")],
    State("locale-store", "data"),
    prevent_initial_call=True,
)
def update_results(result: dict | None, sessions: list, locale: str):
    """Update the results display."""
    if not result:
        return html.Div()

    t = lambda key: get_translation(locale, key)
    sessions = sessions or []

    children = []

    # Charts row
    charts_row = [
        # Radar chart
        html.Div(
            [
                html.H3(t("current_session")),
                dcc.Graph(
                    figure=create_radar_chart(result["metrics"], locale),
                    config={"displayModeBar": False},
                ),
            ],
            className="chart-container",
        ),
    ]

    # Add time series if multiple sessions
    if len(sessions) > 1:
        charts_row.append(
            html.Div(
                [
                    html.H3(t("todays_sessions")),
                    dcc.Graph(
                        figure=create_time_series_chart(sessions, locale),
                        config={"displayModeBar": False},
                    ),
                ],
                className="chart-container",
            )
        )

    children.append(html.Div(charts_row, className="charts-row"))

    # Analysis report
    report = result.get("report", {})
    children.append(
        html.Div(
            [
                html.H3(t("analysis_report")),
                html.Div(
                    [
                        html.H4(t("summary")),
                        html.P(report.get("summary", "")),
                    ],
                    className="report-section",
                ),
                html.Div(
                    [
                        html.H4(t("key_emotions")),
                        html.P(report.get("key_emotions", "")),
                    ],
                    className="report-section",
                ),
                html.Div(
                    [
                        html.H4(t("concerns_themes")),
                        html.P(report.get("concerns_themes", "")),
                    ],
                    className="report-section",
                ),
                html.Div(
                    [
                        html.H4(t("insights")),
                        html.P(report.get("insights", "")),
                    ],
                    className="report-section",
                ),
            ],
            className="analysis-report",
        )
    )

    # Transcription
    children.append(
        html.Div(
            [
                html.H4(t("transcription")),
                html.P(result.get("transcription", ""), className="transcription-text"),
            ],
            className="transcription-section",
        )
    )

    # Session counter
    children.append(
        html.Div(
            f"{t('sessions_today')}: {len(sessions)}",
            className="session-counter",
        )
    )

    # Disclaimer
    children.append(
        html.Div(
            t("disclaimer"),
            className="disclaimer",
        )
    )

    return html.Div(children)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
