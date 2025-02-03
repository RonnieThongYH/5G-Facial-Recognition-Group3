import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import base64
import os
import flask
import threading
import time
import subprocess  # To run the matplot.py script

# Paths to files
LOG_FILE_PATH = r"C:\Users\chean\Downloads\5G-Facial-Recognition-Group3\5G-Facial-Recognition-Group3\recognition_logs.csv"
FRAME_FILE_PATH = r"C:\Users\chean\Downloads\5G-Facial-Recognition-Group3\5G-Facial-Recognition-Group3\latest_frame.jpg"
BAR_CHART_PATH = r"C:\Users\chean\Downloads\5G-Facial-Recognition-Group3\5G-Facial-Recognition-Group3\latest_bar_chart.png"

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "5G Facial Recognition Dashboard"

# Serve the CSV file download
@app.server.route('/download')
def download_csv():
    return flask.send_file(LOG_FILE_PATH, as_attachment=True)

# Function to generate the bar chart using matplot.py
def generate_bar_chart():
    subprocess.run(['python', 'matplot.py'])  # Run matplot.py in a separate process

# Function to run the matplot.py in the background
def background_matplot():
    while True:
        generate_bar_chart()
        time.sleep(30)  # Run it every 30 seconds

# Start the background thread for generating the bar chart
thread = threading.Thread(target=background_matplot, daemon=True)
thread.start()

# Define the app layout
app.layout = html.Div(
    children=[
        html.H1("5G Facial Recognition Door Access System", style={"textAlign": "center"}),

        # Interval for live updates (for the live stream)
        dcc.Interval(
            id="interval-component",
            interval=500,
            n_intervals=0
        ),

        # Live feed and bar chart side by side
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H4("Live Stream"),
                        html.Img(id="live-feed", style={"maxWidth": "640px", "maxHeight": "480px", "display": "block", "margin": "0 auto"})
                    ],
                    style={"width": "48%", "display": "inline-block", "verticalAlign": "top"}
                ),
                html.Div(
                    children=[
                        html.H4("Top Recognized Faces"),
                        html.Img(id="bar-chart", style={"maxWidth": "640px", "maxHeight": "480px", "display": "block", "margin": "0 auto"})
                    ],
                    style={"width": "48%", "display": "inline-block", "verticalAlign": "top"}
                )
            ],
            style={"display": "flex", "justifyContent": "space-between", "marginBottom": "20px"}
        ),

        # Metrics
        html.Div(
            id="metrics",
            children=[
                html.Div(
                    children=[
                        html.H4("Recognized Faces"),
                        html.P(id="recognized-count", style={"fontSize": "2em", "fontWeight": "bold"})
                    ],
                    style={"flex": "1", "padding": "10px", "border": "1px solid #ccc", "borderRadius": "5px"}
                ),
                html.Div(
                    children=[
                        html.H4("Unrecognized Faces"),
                        html.P(id="unrecognized-count", style={"fontSize": "2em", "fontWeight": "bold"})
                    ],
                    style={"flex": "1", "padding": "10px", "border": "1px solid #ccc", "borderRadius": "5px"}
                ),
            ],
            style={"display": "flex", "gap": "20px", "marginBottom": "20px"}
        ),

        # Logs and Charts
        html.Div(
            id="logs-section",
            children=[
                html.H4("Recognition Logs"),
                dash_table.DataTable(
                    id="logs-table",
                    columns=[
                        {"name": "Timestamp", "id": "Timestamp"},
                        {"name": "Name", "id": "Name"},
                        {"name": "Status", "id": "Status"}
                    ],
                    style_table={"overflowX": "auto"},
                    style_cell={"textAlign": "left"},
                    style_header={"fontWeight": "bold"},
                    sort_action="native"  # Enable sorting
                ),
            ],
            style={"maxHeight": "300px", "overflowY": "scroll", "marginBottom": "20px"}
        ),

        # Download Button
        html.Div(
            children=[
                html.A(
                    html.Button("Download Logs as CSV", id="download-btn", n_clicks=0),
                    href="/download",
                    target="_blank",
                    style={"marginTop": "20px"}
                )
            ],
            style={"textAlign": "center"}
        )
    ],
    style={"padding": "20px", "fontFamily": "Arial, sans-serif"}
)

@app.callback(
    [Output("recognized-count", "children"),
     Output("unrecognized-count", "children"),
     Output("logs-table", "data"),
     Output("live-feed", "src"),
     Output("bar-chart", "src")],  # Output for the bar chart image
    [Input("interval-component", "n_intervals")]
)
def update_dashboard(_):
    recognized_count, unrecognized_count, logs = 0, 0, []

    if os.path.exists(LOG_FILE_PATH):
        logs_df = pd.read_csv(LOG_FILE_PATH)

        # Clean up the logs by dropping empty rows or rows with missing data
        logs_df = logs_df.dropna(subset=["Name", "Status"])  # Drop rows where "Name" or "Status" is missing
        logs_df = logs_df[logs_df["Name"].str.strip() != ""]  # Remove rows with empty "Name" fields

        # Count the total recognized faces
        recognized_count = logs_df[logs_df["Status"] == "Recognized"].shape[0]
        # Count the total unrecognized faces
        unrecognized_count = logs_df[logs_df["Status"] == "Not Recognized"].shape[0]

        # Sort logs by most recent
        logs_df.sort_values("Timestamp", ascending=False, inplace=True)  # Sort logs by most recent
        logs = logs_df.to_dict("records")

    # Prepare the live feed image
    frame_src = None
    if os.path.exists(FRAME_FILE_PATH):
        with open(FRAME_FILE_PATH, "rb") as image_file:
            frame_src = "data:image/jpeg;base64," + base64.b64encode(image_file.read()).decode("utf-8")

    # Prepare the bar chart image
    bar_chart_src = None
    if os.path.exists(BAR_CHART_PATH):
        with open(BAR_CHART_PATH, "rb") as image_file:
            bar_chart_src = "data:image/png;base64," + base64.b64encode(image_file.read()).decode("utf-8")

    return recognized_count, unrecognized_count, logs, frame_src, bar_chart_src

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
