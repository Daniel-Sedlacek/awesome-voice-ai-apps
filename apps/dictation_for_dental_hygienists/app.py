"""
Dental Dictation Application
A Dash app for dental hygienists to dictate periodontal examination findings.
Supports English, German, and Czech languages.
"""

import base64
from dash import Dash, html, dcc, callback, Output, Input, State, clientside_callback

from languages import get_language_options, get_example_dictation
from azure_services import transcribe_audio_continuous, AzureServiceError
from extraction_service import extract_periodontal_data, ExtractionError, exam_to_dict
from dental_chart import create_dental_chart_component, create_results_summary
from data_models import PeriodontalExam

# Initialize Dash app
app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# Language options for dropdown
LANGUAGE_OPTIONS = [
    {"label": name, "value": locale}
    for locale, name in get_language_options()
]

# App layout
app.layout = html.Div(
    [
        # Header
        html.Div(
            [
                html.H1("Dental Dictation"),
                html.P("Dictate periodontal examination findings and see structured results."),
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
                            children="0:00",
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
        # Example dictation section
        html.Div(
            [
                html.H3("Example dictation:"),
                html.P(
                    id="example-dictation",
                    children=get_example_dictation("en-US"),
                    className="example-text",
                ),
            ],
            className="example-section",
        ),
        # Dental chart
        html.Div(
            id="dental-chart-container",
            children=create_dental_chart_component(None),
            className="chart-wrapper",
        ),
        # Results section
        html.Div(
            id="results-container",
            className="results-section",
        ),
        # Hidden stores for state management
        dcc.Store(id="recording-state", data={"isRecording": False}),
        dcc.Store(id="audio-data-store", data=None),
        dcc.Store(id="exam-data-store", data=None),
        dcc.Interval(id="timer-interval", interval=1000, disabled=True),
    ],
    className="app-container",
)


# Clientside callback for handling recording start/stop
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
            return "0:00";
        }
        const state = window.dashAudioRecorder.getRecordingState();
        const elapsed = Math.floor(state.elapsed);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        return minutes + ":" + (seconds < 10 ? "0" : "") + seconds;
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
    Output("example-dictation", "children"),
    Input("language-selector", "value"),
)
def update_example_dictation(language: str):
    """Update the example dictation text when language changes."""
    return get_example_dictation(language)


@callback(
    [
        Output("exam-data-store", "data"),
        Output("status-display", "children", allow_duplicate=True),
        Output("status-display", "className", allow_duplicate=True),
    ],
    Input("audio-data-store", "data"),
    State("language-selector", "value"),
    prevent_initial_call=True,
)
def process_audio(audio_data: str | None, language: str):
    """Process recorded audio: transcribe and extract data."""
    if not audio_data:
        return None, "Ready to record", "status-display ready"

    try:
        # Decode base64 audio data
        audio_bytes = base64.b64decode(audio_data)

        # Transcribe using Azure Speech-to-Text
        transcription = transcribe_audio_continuous(audio_bytes, language)

        if not transcription.strip():
            return None, "No speech detected. Please try again.", "status-display error"

        # Extract periodontal data using LLM
        exam = extract_periodontal_data(transcription)

        # Convert to dict for storage
        exam_dict = exam_to_dict(exam)

        return (
            exam_dict,
            f"Extracted data for {len(exam.teeth)} tooth/teeth",
            "status-display success",
        )

    except AzureServiceError as e:
        return None, f"Transcription error: {str(e)}", "status-display error"
    except ExtractionError as e:
        return None, f"Extraction error: {str(e)}", "status-display error"
    except Exception as e:
        return None, f"Error: {str(e)}", "status-display error"


@callback(
    Output("dental-chart-container", "children"),
    Input("exam-data-store", "data"),
    prevent_initial_call=True,
)
def update_dental_chart(exam_data: dict | None):
    """Update the dental chart visualization."""
    if not exam_data:
        return create_dental_chart_component(None)

    # Convert dict back to PeriodontalExam
    exam = PeriodontalExam(**exam_data)
    return create_dental_chart_component(exam)


@callback(
    Output("results-container", "children"),
    Input("exam-data-store", "data"),
    prevent_initial_call=True,
)
def update_results(exam_data: dict | None):
    """Update the results summary."""
    if not exam_data:
        return html.Div()

    # Convert dict back to PeriodontalExam
    exam = PeriodontalExam(**exam_data)
    return create_results_summary(exam)


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8051)
