import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams['text.usetex'] = True
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']  # LNCS compatible font

# Define the new color palette based on your specifications
color_palette = [
    '#4E79A7',  # Light coral
    '#F28E2B',  # Coral
    '#59A14F',  # Dark coral
    '#EDC948',  # Lighter dark coral
    '#B07AA1',  # Darker coral
    '#76B7B2'   # Even darker coral
]  

def get_all_files(input_folder):
    """Returns a list of all CSV files in the input folder."""
    files = [f for f in os.listdir(input_folder) if f.endswith(".csv")]
    return files

def process_csv_file(csv_file_path):
    """Reads the CSV file, calculates the desired values, and returns the data."""
    df = pd.read_csv(csv_file_path)

    # Drop rows with NaN in the 'runs' column
    df_clean = df.dropna(subset=['runs'])

    # Group by 'runs' and aggregate directly
    df_grouped = df_clean.groupby('runs').agg(
        consensus_tps=('consensus_tps', 'max'), 
        consensus_latency=('consensus_latency', 'min')
    ).reset_index()
    
    # Define configurations
    config = ['1 (PoS)', r'$\lambda = 0.9$', r'$\lambda = 0.8$', 
              r'$\lambda = 0.7$', r'$\lambda = 0.6$', r'$\lambda = 0.5$']
    
    # Add the 'config' column
    df_grouped['config'] = config

    return df_grouped

def plot_combined(all_data_hotstuff, all_data_cometbft, output_folder):
    """Plots both TPS and latency data in a combined figure with four subplots."""
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))  # Create a figure with four subplots

    # Number of blockchains
    num_blockchains_hotstuff = len(all_data_hotstuff)  
    num_blockchains_cometbft = len(all_data_cometbft)  
    num_lambda = 6  # Number of lambda values

    # X locations for blockchains
    x_hotstuff = np.arange(num_blockchains_hotstuff)  
    x_cometbft = np.arange(num_blockchains_cometbft)  

    # Initialize empty lists to hold the bar positions for TPS and Latency
    bar_positions_tps_hotstuff = np.zeros((num_lambda, num_blockchains_hotstuff))
    bar_positions_latency_hotstuff = np.zeros((num_lambda, num_blockchains_hotstuff))
    
    bar_positions_tps_cometbft = np.zeros((num_lambda, num_blockchains_cometbft))
    bar_positions_latency_cometbft = np.zeros((num_lambda, num_blockchains_cometbft))

    # Collect data for Hotstuff plots
    for i, (data, csv_file) in enumerate(all_data_hotstuff):
        for j in range(num_lambda):
            bar_positions_tps_hotstuff[j, i] = data['consensus_tps'].iloc[j]
            bar_positions_latency_hotstuff[j, i] = data['consensus_latency'].iloc[j]

    # Collect data for CometBFT plots
    for i, (data, csv_file) in enumerate(all_data_cometbft):
        for j in range(num_lambda):
            bar_positions_tps_cometbft[j, i] = data['consensus_tps'].iloc[j]
            bar_positions_latency_cometbft[j, i] = data['consensus_latency'].iloc[j]

    bar_width = 0.15  # Width of the bars

    # Plot TPS data for Hotstuff
    for j in range(num_lambda):
        axs[0, 0].bar(x_hotstuff + j * bar_width, bar_positions_tps_hotstuff[j], width=bar_width, 
                       label=r'$\lambda = %.1f$' % (1 - j * 0.1) if j != 0 else r'\textbf{PoS} ($\lambda=1$)', 
                       color=color_palette[j % len(color_palette)])  

    # Configure Hotstuff TPS plot
    axs[0, 0].set_xticks(x_hotstuff + bar_width * (num_lambda - 1) / 2)
    axs[0, 0].set_xticklabels([data['blockchain'].iloc[0] for data, _ in all_data_hotstuff], fontsize=15)
    axs[0, 0].set_ylabel(r'\textbf{Consensus TPS}', fontsize=20)
    axs[0, 0].set_ylim(np.min(bar_positions_tps_cometbft) * 0.6, np.max(bar_positions_tps_hotstuff) * 1.05)
    axs[0, 0].grid(axis='y', linestyle='--', alpha=0.7)  # Add y-axis grid lines
    axs[0, 0].tick_params(axis='y', labelsize=20)  # Set y-tick label size to 20
    axs[0, 0].set_title(r'\textbf{Hotstuff Consensus TPS}', fontsize=20)

    # Plot TPS data for CometBFT
    for j in range(num_lambda):
        axs[0, 1].bar(x_cometbft + j * bar_width, bar_positions_tps_cometbft[j], width=bar_width, 
                       label=r'$\lambda = %.1f$' % (1 - j * 0.1) if j != 0 else r'\textbf{PoS} ($\lambda=1$)', 
                       color=color_palette[j % len(color_palette)])  

    # Configure CometBFT TPS plot
    axs[0, 1].set_xticks(x_cometbft + bar_width * (num_lambda - 1) / 2)
    axs[0, 1].set_xticklabels([data['blockchain'].iloc[0] for data, _ in all_data_cometbft], fontsize=15)
    axs[0, 1].set_ylabel(r'\textbf{Consensus TPS}', fontsize=20)
    axs[0, 1].set_ylim(np.min(bar_positions_tps_cometbft) * 0.6, np.max(bar_positions_tps_cometbft) * 1.05)
    axs[0, 1].grid(axis='y', linestyle='--', alpha=0.7)  # Add y-axis grid lines
    axs[0, 1].tick_params(axis='y', labelsize=20)  # Set y-tick label size to 20
    axs[0, 1].set_title(r'\textbf{CometBFT Consensus TPS}', fontsize=20)

    # Plot Latency data for Hotstuff
    for j in range(num_lambda):
        axs[1, 0].bar(x_hotstuff + j * bar_width, bar_positions_latency_hotstuff[j], width=bar_width, 
                       label=r'$\lambda = %.1f$' % (1 - j * 0.1) if j != 0 else r'\textbf{PoS} ($\lambda=1$)', 
                       color=color_palette[j % len(color_palette)])  

    # Configure Hotstuff Latency plot
    axs[1, 0].set_xticks(x_hotstuff + bar_width * (num_lambda - 1) / 2)
    axs[1, 0].set_xticklabels([data['blockchain'].iloc[0] for data, _ in all_data_hotstuff], fontsize=15)
    axs[1, 0].set_ylabel(r'\textbf{Consensus latency (ms)}', fontsize=20)
    axs[1, 0].tick_params(axis='y', labelsize=20)  # Set y-tick label size to 20
    axs[1, 0].grid(axis='y', linestyle='--', alpha=0.7)  # Add y-axis grid lines

    # Plot Latency data for CometBFT
    for j in range(num_lambda):
        axs[1, 1].bar(x_cometbft + j * bar_width, bar_positions_latency_cometbft[j], width=bar_width, 
                       label=r'$\lambda = %.1f$' % (1 - j * 0.1) if j != 0 else r'\textbf{PoS} ($\lambda=1$)', 
                       color=color_palette[j % len(color_palette)])  

    # Configure CometBFT Latency plot
    axs[1, 1].set_xticks(x_cometbft + bar_width * (num_lambda - 1) / 2)
    axs[1, 1].set_xticklabels([data['blockchain'].iloc[0] for data, _ in all_data_cometbft], fontsize=15)
    axs[1, 1].set_ylabel(r'\textbf{Consensus latency (ms)}', fontsize=20)
    axs[1, 1].tick_params(axis='y', labelsize=20)  # Set y-tick label size to 20
    axs[1, 1].grid(axis='y', linestyle='--', alpha=0.7)  # Add y-axis grid lines

    # Add titles to each column
    axs[0, 0].set_title(r'\textbf{Hotstuff}', fontsize=28)
    axs[0, 1].set_title(r'\textbf{CometBFT}', fontsize=28)

    # Create a single legend for all plots and position it at the bottom
    handles, labels = axs[1, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', fontsize=20,  ncol=num_lambda)

    plt.tight_layout()
    plt.subplots_adjust(top=0.85, bottom=0.15)  # Adjust top to fit the main title and bottom for legend

    plot_filename = os.path.join(output_folder, "combined_plot_all.pdf")
    plt.savefig(plot_filename, format='pdf', dpi=300, transparent=True)
    plt.close()  # Close the plot to free memory

    print(f"Combined plot saved to {plot_filename}")


# Define the input and output folders for Hotstuff and CometBFT
input_folder_hotstuff = 'data/geodec_hotstuff_2'
input_folder_cometbft = 'data/geodec_cometbft'
output_folder_base = 'results/geodec/plots'

# Get all CSV files from the input folders
csv_files_hotstuff = get_all_files(input_folder_hotstuff)
csv_files_cometbft = get_all_files(input_folder_cometbft)

# List to store data from all CSV files
all_data_hotstuff = []
all_data_cometbft = []

# Process each CSV file and collect the data for Hotstuff
for csv_file in csv_files_hotstuff:
    csv_file_path = os.path.join(input_folder_hotstuff, csv_file)
    chain = csv_file.replace('.csv', '').capitalize()

    df = process_csv_file(csv_file_path) 
    print(chain)
    if chain == 'Ethernodes':
        chain = 'Ethereum\nnodes'
    df['blockchain'] = chain
    all_data_hotstuff.append((df, csv_file_path))

# Sort all_data by blockchain name for Hotstuff
all_data_hotstuff.sort(key=lambda x: x[0]['blockchain'].iloc[0])  

# Process each CSV file and collect the data for CometBFT
for csv_file in csv_files_cometbft:
    csv_file_path = os.path.join(input_folder_cometbft, csv_file)
    chain = csv_file.replace('.csv', '').capitalize()

    df = process_csv_file(csv_file_path) 
    if chain == 'Ethernodes':
        chain = 'Ethereum\nnodes'
    df['blockchain'] = chain
    all_data_cometbft.append((df, csv_file_path))

# Sort all_data by blockchain name for CometBFT
all_data_cometbft.sort(key=lambda x: x[0]['blockchain'].iloc[0])  

# print(all_data_hotstuff)
# print(all_data_cometbft)

# # Create an output folder if it doesn't exist
if not os.path.exists(output_folder_base):
    os.makedirs(output_folder_base)

# # Generate and save the combined plots for both Hotstuff and CometBFT
plot_combined(all_data_hotstuff, all_data_cometbft, output_folder_base)
