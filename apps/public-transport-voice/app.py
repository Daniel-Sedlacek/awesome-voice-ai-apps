"""
Public Transport Voice Translation Application
A Dash app for real-time speech translation using Azure Cognitive Services.
"""

import base64
import json
from dash import Dash, html, dcc, callback, Output, Input, State, clientside_callback
from flask import request

from languages import get_language_options, get_language_name
from azure_services import process_recording, AzureServiceError

# Initialize Dash app
app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# Get language options for dropdowns
LANGUAGE_OPTIONS = [{"label": name, "value": locale} for locale, name in get_language_options()]

# App layout
app.layout = html.Div(
    [
        # Header
        html.H1("Voice Translation", style={"textAlign": "center", "marginBottom": "20px"}),
        html.P(
            "Speak in one language, hear it translated to two others.",
            style={"textAlign": "center", "color": "#666", "marginBottom": "30px"},
        ),
        # Usage counter
        html.Div(
            id="usage-display",
            style={
                "textAlign": "center",
                "marginBottom": "20px",
                "padding": "10px",
                "backgroundColor": "#f0f0f0",
                "borderRadius": "5px",
            },
        ),
        # Language selection
        html.Div(
            [
                # Source language (STT)
                html.Div(
                    [
                        html.Label("Speak in:", style={"fontWeight": "bold"}),
                        dcc.Dropdown(
                            id="source-language",
                            options=LANGUAGE_OPTIONS,
                            value="en-US",
                            clearable=False,
                            style={"width": "100%"},
                        ),
                    ],
                    style={"flex": "1", "padding": "10px"},
                ),
                # Target language 1
                html.Div(
                    [
                        html.Label("Translate to (1):", style={"fontWeight": "bold"}),
                        dcc.Dropdown(
                            id="target-language-1",
                            options=LANGUAGE_OPTIONS,
                            value="es-ES",
                            clearable=False,
                            style={"width": "100%"},
                        ),
                    ],
                    style={"flex": "1", "padding": "10px"},
                ),
                # Target language 2
                html.Div(
                    [
                        html.Label("Translate to (2):", style={"fontWeight": "bold"}),
                        dcc.Dropdown(
                            id="target-language-2",
                            options=LANGUAGE_OPTIONS,
                            value="fr-FR",
                            clearable=False,
                            style={"width": "100%"},
                        ),
                    ],
                    style={"flex": "1", "padding": "10px"},
                ),
            ],
            style={
                "display": "flex",
                "justifyContent": "center",
                "flexWrap": "wrap",
                "marginBottom": "30px",
            },
        ),
        # Recording button and timer
        html.Div(
            [
                html.Button(
                    "Start Recording",
                    id="record-button",
                    n_clicks=0,
                    style={
                        "padding": "15px 40px",
                        "fontSize": "18px",
                        "backgroundColor": "#4CAF50",
                        "color": "white",
                        "border": "none",
                        "borderRadius": "25px",
                        "cursor": "pointer",
                        "marginRight": "20px",
                    },
                ),
                html.Div(
                    id="timer-display",
                    children="10s",
                    style={
                        "fontSize": "24px",
                        "fontWeight": "bold",
                        "display": "inline-block",
                        "minWidth": "60px",
                    },
                ),
            ],
            style={"textAlign": "center", "marginBottom": "30px"},
        ),
        # Status display
        html.Div(
            id="status-display",
            children="Ready to record",
            style={
                "textAlign": "center",
                "padding": "15px",
                "marginBottom": "20px",
                "backgroundColor": "#e7f3ff",
                "borderRadius": "5px",
                "fontSize": "16px",
            },
        ),
        # Transcription results
        html.Div(
            id="results-container",
            style={"marginTop": "30px"},
        ),
        # Hidden stores for state management
        dcc.Store(id="recording-state", data={"isRecording": False}),
        dcc.Store(id="audio-data-store", data=None),
        dcc.Store(id="processing-result", data=None),
        dcc.Interval(id="timer-interval", interval=100, disabled=True),
        # Hidden div for triggering audio playback
        html.Div(id="audio-player-trigger", style={"display": "none"}),
    ],
    style={
        "maxWidth": "900px",
        "margin": "0 auto",
        "padding": "20px",
        "fontFamily": "Arial, sans-serif",
    },
)


# Clientside callback for handling recording start/stop
clientside_callback(
    """
    async function(n_clicks, recordingState) {
        if (!n_clicks) {
            return [window.dash_clientside.no_update, window.dash_clientside.no_update,
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
                    "Recording..."
                ];
            } else {
                return [
                    {isRecording: false},
                    null,
                    true,
                    "Error: " + (result.error || "Could not access microphone")
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
                    "Processing..."
                ];
            } else {
                return [
                    {isRecording: false},
                    null,
                    true,
                    "Error: " + (result.error || "Recording failed")
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
            return "10s";
        }
        const state = window.dashAudioRecorder.getRecordingState();
        return Math.ceil(state.remaining) + "s";
    }
    """,
    Output("timer-display", "children"),
    Input("timer-interval", "n_intervals"),
    State("recording-state", "data"),
)


# Clientside callback for updating button style
clientside_callback(
    """
    function(recordingState) {
        const isRecording = recordingState?.isRecording || false;
        if (isRecording) {
            return {
                padding: "15px 40px",
                fontSize: "18px",
                backgroundColor: "#f44336",
                color: "white",
                border: "none",
                borderRadius: "25px",
                cursor: "pointer",
                marginRight: "20px"
            };
        } else {
            return {
                padding: "15px 40px",
                fontSize: "18px",
                backgroundColor: "#4CAF50",
                color: "white",
                border: "none",
                borderRadius: "25px",
                cursor: "pointer",
                marginRight: "20px"
            };
        }
    }
    """,
    Output("record-button", "style"),
    Input("recording-state", "data"),
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
        Output("processing-result", "data"),
        Output("status-display", "children", allow_duplicate=True),
    ],
    Input("audio-data-store", "data"),
    [
        State("source-language", "value"),
        State("target-language-1", "value"),
        State("target-language-2", "value"),
    ],
    prevent_initial_call=True,
)
def process_audio(audio_data, source_lang, target_lang_1, target_lang_2):
    """Process the recorded audio through Azure services."""
    if not audio_data:
        return None, "Ready to record"

    try:
        # Decode base64 audio data
        audio_bytes = base64.b64decode(audio_data)

        # Process through Azure services
        result = process_recording(audio_bytes, source_lang, target_lang_1, target_lang_2)

        return result, "Processing complete! Playing audio..."

    except AzureServiceError as e:
        return None, f"Error: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"


@callback(
    Output("results-container", "children"),
    Input("processing-result", "data"),
    prevent_initial_call=True,
)
def display_results(result):
    """Display transcription and translation results."""
    if not result:
        return html.Div()

    def create_result_card(title, text, locale):
        lang_name = get_language_name(locale)
        return html.Div(
            [
                html.H3(f"{title} ({lang_name})", style={"marginBottom": "10px", "color": "#333"}),
                html.P(text, style={"fontSize": "16px", "lineHeight": "1.6"}),
            ],
            style={
                "padding": "20px",
                "marginBottom": "15px",
                "backgroundColor": "#f9f9f9",
                "borderRadius": "8px",
                "borderLeft": "4px solid #4CAF50",
            },
        )

    return html.Div(
        [
            create_result_card("Original", result["original"]["text"], result["original"]["locale"]),
            create_result_card(
                "Translation 1", result["translation_1"]["text"], result["translation_1"]["locale"]
            ),
            create_result_card(
                "Translation 2", result["translation_2"]["text"], result["translation_2"]["locale"]
            ),
        ]
    )


# Clientside callback for playing audio sequence
clientside_callback(
    """
    async function(result) {
        if (!result) {
            return "";
        }

        // Collect audio data in order: original, translation 1, translation 2
        const audioSequence = [
            result.original.audio_base64,
            result.translation_1.audio_base64,
            result.translation_2.audio_base64
        ];

        // Play with 1.5 second delay between each
        await window.dashAudioRecorder.playAudioSequence(audioSequence, 1500);

        return "done";
    }
    """,
    Output("audio-player-trigger", "children"),
    Input("processing-result", "data"),
    prevent_initial_call=True,
)


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port="8050")
