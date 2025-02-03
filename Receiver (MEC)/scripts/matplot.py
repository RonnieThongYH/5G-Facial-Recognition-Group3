import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for matplotlib
import matplotlib.pyplot as plt
import os

LOG_FILE_PATH = r"C:\Users\chean\Downloads\5G-Facial-Recognition-Group3\5G-Facial-Recognition-Group3\recognition_logs.csv"
BAR_CHART_PATH = r"C:\Users\chean\Downloads\5G-Facial-Recognition-Group3\5G-Facial-Recognition-Group3\latest_bar_chart.png"

def generate_bar_chart():
    # Read the logs from CSV
    if os.path.exists(LOG_FILE_PATH):
        logs_df = pd.read_csv(LOG_FILE_PATH)

        # Count the occurrences of each recognized face
        top_recognized_faces = logs_df[logs_df["Status"] == "Recognized"]['Name'].value_counts().reset_index()
        top_recognized_faces.columns = ['Name', 'Recognized Count']

        # Create the bar chart using Matplotlib
        plt.figure(figsize=(10, 6))
        plt.bar(top_recognized_faces['Name'], top_recognized_faces['Recognized Count'], color='skyblue')
        plt.xlabel('Name')
        plt.ylabel('Recognized Count')
        plt.title('Top Recognized Faces')

        # Save the chart as a PNG image
        plt.savefig(BAR_CHART_PATH)
        plt.close()  # Close the plot to free up memory

# Run the bar chart generation function
if __name__ == "__main__":
    generate_bar_chart()
