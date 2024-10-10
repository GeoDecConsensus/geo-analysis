import os

import matplotlib.pyplot as plt
import pandas as pd


def get_all_files(input_folder):
    """
    Returns a list of all CSV files in the input folder.
    """
    files = [f for f in os.listdir(input_folder) if f.endswith(".csv")]
    return files

def plot_and_save(csv_file_path, output_folder):
    """
    Reads the CSV file, cleans it, generates plots, and saves them.
    """
    # Read the CSV file
    df = pd.read_csv(csv_file_path)

    # Remove rows where 'runs' column has missing values
    df_clean = df.dropna(subset=['runs'])

    # Define titles for each run
    titles = ['stake_weight', '0.9linear_weight', '0.8linear_weight', '0.7linear_weight', '0.6linear_weight', '0.5linear_weight']
    df_clean['title'] = titles

    # Plot graphs
    plt.figure(figsize=(15, 10))

    # Plot for consensus_tps
    plt.subplot(2, 2, 1)
    plt.plot(df_clean['title'], df_clean['consensus_tps'], marker='o')
    plt.title('Consensus TPS')
    plt.xticks(rotation=45, ha="right")
    plt.xlabel('Tests')
    plt.ylabel('TPS')

    # Plot for consensus_latency
    plt.subplot(2, 2, 2)
    plt.plot(df_clean['title'], df_clean['consensus_latency'], marker='o', color='orange')
    plt.title('Consensus Latency')
    plt.xticks(rotation=45, ha="right")
    plt.xlabel('Tests')
    plt.ylabel('Latency')

    # Plot for end_to_end_tps
    plt.subplot(2, 2, 3)
    plt.plot(df_clean['title'], df_clean['end_to_end_tps'], marker='o', color='green')
    plt.title('End-to-End TPS')
    plt.xticks(rotation=45, ha="right")
    plt.xlabel('Tests')
    plt.ylabel('TPS')

    # Plot for end_to_end_latency
    plt.subplot(2, 2, 4)
    plt.plot(df_clean['title'], df_clean['end_to_end_latency'], marker='o', color='red')
    plt.title('End-to-End Latency')
    plt.xticks(rotation=45, ha="right")
    plt.xlabel('Tests')
    plt.ylabel('Latency')

    plt.tight_layout()

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Generate the name for the output plot
    plot_filename = os.path.join(output_folder, f"{os.path.basename(csv_file_path).replace('.csv', '')}_plots.png")

    # Save the plot to a file
    plt.savefig(plot_filename)
    plt.close()

    print(f"Plots saved to {plot_filename}")

# Define the input and output folders
input_folder = 'data/geodec_run_2'
output_folder_base = 'data/geodec_run_2/plots'

# Get all CSV files from the input folder
csv_files = get_all_files(input_folder)

# Loop through each CSV file, generate and save the plots
for csv_file in csv_files:
    csv_file_path = os.path.join(input_folder, csv_file)
    
    # Create an output folder specific for each CSV file's plots
    output_folder = os.path.join(output_folder_base)
    
    # Generate and save the plots for this CSV file
    plot_and_save(csv_file_path, output_folder)