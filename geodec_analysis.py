import os

import matplotlib.pyplot as plt
import pandas as pd


def get_all_files(input_folder):
    """
    Returns a list of all CSV files in the input folder.
    """
    files = [f for f in os.listdir(input_folder) if f.endswith(".csv")]
    return files

def plot_and_save(df, csv_file_path, output_folder, agg_type):
    """
    Generates plots for the aggregated data (median or max) and saves them.
    """
    titles = ['stake_weight', '0.9linear_weight', '0.8linear_weight', '0.7linear_weight', '0.6linear_weight', '0.5linear_weight']
    df['title'] = titles

    plt.figure(figsize=(15, 10))

    # Plot for consensus_tps
    plt.subplot(2, 2, 1)
    plt.plot(df['title'], df['consensus_tps'], marker='o')
    plt.title(f'Consensus TPS ({agg_type})')
    plt.xticks(rotation=45, ha="right")
    plt.xlabel('Tests')
    plt.ylabel('TPS')

    # Plot for consensus_latency
    plt.subplot(2, 2, 2)
    plt.plot(df['title'], df['consensus_latency'], marker='o', color='orange')
    plt.title(f'Consensus Latency ({agg_type})')
    plt.xticks(rotation=45, ha="right")
    plt.xlabel('Tests')
    plt.ylabel('Latency')

    # Plot for end_to_end_tps
    plt.subplot(2, 2, 3)
    plt.plot(df['title'], df['end_to_end_tps'], marker='o', color='green')
    plt.title(f'End-to-End TPS ({agg_type})')
    plt.xticks(rotation=45, ha="right")
    plt.xlabel('Tests')
    plt.ylabel('TPS')

    # Plot for end_to_end_latency
    plt.subplot(2, 2, 4)
    plt.plot(df['title'], df['end_to_end_latency'], marker='o', color='red')
    plt.title(f'End-to-End Latency ({agg_type})')
    plt.xticks(rotation=45, ha="right")
    plt.xlabel('Tests')
    plt.ylabel('Latency')

    plt.tight_layout()

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Generate the name for the output plot
    plot_filename = os.path.join(output_folder, f"{os.path.basename(csv_file_path).replace('.csv', '')}_{agg_type}_plots.png")

    # Save the plot to a file
    plt.savefig(plot_filename)
    plt.close()

    print(f"{agg_type.capitalize()} plots saved to {plot_filename}")

def process_csv_file(csv_file_path, output_folder):
    """
    Reads the CSV file, calculates the median and max values for each 'runs' group,
    generates plots, and saves them.
    """
    # Read the CSV file
    df = pd.read_csv(csv_file_path)

    # Remove rows where 'runs' column has missing values
    df_clean = df.dropna(subset=['runs'])

    # Group by 'runs' and calculate median and max values for the metrics
    agg_funcs = {'consensus_tps': ['median', 'max'], 
                 'consensus_latency': ['median', 'max'], 
                 'end_to_end_tps': ['median', 'max'], 
                 'end_to_end_latency': ['median', 'max']}

    df_grouped = df_clean.groupby('runs').agg(agg_funcs)

    # Flatten multi-level columns
    df_grouped.columns = ['_'.join(col) for col in df_grouped.columns]

    # Calculate and plot median values
    df_median = df_grouped[['consensus_tps_median', 'consensus_latency_median', 'end_to_end_tps_median', 'end_to_end_latency_median']].reset_index()
    df_median.columns = ['runs', 'consensus_tps', 'consensus_latency', 'end_to_end_tps', 'end_to_end_latency']
    plot_and_save(df_median, csv_file_path, output_folder, 'median')

    # Calculate and plot max values
    df_max = df_grouped[['consensus_tps_max', 'consensus_latency_max', 'end_to_end_tps_max', 'end_to_end_latency_max']].reset_index()
    df_max.columns = ['runs', 'consensus_tps', 'consensus_latency', 'end_to_end_tps', 'end_to_end_latency']
    plot_and_save(df_max, csv_file_path, output_folder, 'max')

# Define the input and output folders
input_folder = 'data/geodec_cometbft'
output_folder_base = 'data/geodec_cometbft/plots'

# Get all CSV files from the input folder
csv_files = get_all_files(input_folder)

# Loop through each CSV file, generate and save the plots
for csv_file in csv_files:
    csv_file_path = os.path.join(input_folder, csv_file)

    # Create an output folder specific for each CSV file's plots
    output_folder = os.path.join(output_folder_base)

    # Generate and save the plots for this CSV file
    process_csv_file(csv_file_path, output_folder)