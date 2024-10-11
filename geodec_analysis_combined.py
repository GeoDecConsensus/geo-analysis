import os

import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams.update(plt.rcParamsDefault)
# Enable LaTeX and set fonts for better formatting
plt.rcParams['text.usetex'] = True
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']  # LNCS compatible font
plt.rcParams['axes.titlesize'] = 14  # Title size for better readability
plt.rcParams['axes.labelsize'] = 12  # Axis labels size
plt.rcParams['xtick.labelsize'] = 10  # X-tick size
plt.rcParams['ytick.labelsize'] = 10  # Y-tick size
plt.rcParams['legend.fontsize'] = 10  # Legend font size
plt.rcParams['figure.titlesize'] = 14  # Figure title size

def get_all_files(input_folder):
    """
    Returns a list of all CSV files in the input folder.
    """
    files = [f for f in os.listdir(input_folder) if f.endswith(".csv")]
    return files

def plot_category_across_files(all_data, category, output_folder, agg_type):
    """
    Plots data for a given category across all CSV files, with clean formatting and alphabetically ordered legend.
    """
    plt.figure(figsize=(10, 6))
    
    # Store labels and data for sorting the legend alphabetically
    lines = []
    labels = []
    
    for data, csv_file in all_data:
        label = os.path.basename(csv_file).replace(".csv", "").title()  # Clean up label by removing .csv and capitalizing
        line, = plt.plot(data['title'], data[category], marker='o', label=label)
        lines.append(line)
        labels.append(label)

    # Sort the legend alphabetically
    sorted_lines_labels = sorted(zip(labels, lines), key=lambda x: x[0])
    sorted_labels = [label for label, _ in sorted_lines_labels]
    sorted_lines = [line for _, line in sorted_lines_labels]
    
    # Configure labels and legend
    plt.ylabel(r'\textbf{' + category.replace("_", " ").capitalize() + '}', fontsize=14)
    plt.xticks(rotation=45, ha="right", fontsize=12)
    plt.yticks(fontsize=12)
    
    # Place legend outside the plot for better clarity
    plt.legend(sorted_lines, sorted_labels, title=r'\textbf{Blockchains}', bbox_to_anchor=(1.05, 1), loc='upper right', frameon=False)

    # Tight layout to prevent text clipping
    plt.tight_layout(rect=[0, 0, 0.85, 1])

    # Save the plot as PDF in the specified folder
    plot_filename = os.path.join(output_folder, f"{category}_{agg_type}.pdf")
    plt.savefig(plot_filename, format='pdf', dpi=300, transparent=True)
    plt.close()  # Close the plot to free memory

    print(f"Comparison plot for {category} ({agg_type}) saved to {plot_filename}")

def process_csv_file(csv_file_path, agg_type):
    """
    Reads the CSV file, calculates the median or max values for each 'runs' group, and returns the data.
    """
    # Read the CSV file
    df = pd.read_csv(csv_file_path)

    # Remove rows where 'runs' column has missing values
    df_clean = df.dropna(subset=['runs'])

    # Group by 'runs' and calculate the chosen aggregation (median or max) for the metrics
    agg_funcs = {'consensus_tps': agg_type, 
                 'consensus_latency': agg_type, 
                 'end_to_end_tps': agg_type, 
                 'end_to_end_latency': agg_type}

    df_grouped = df_clean.groupby('runs').agg(agg_funcs).reset_index()

    # Define titles for each run
    titles = ['1 (PoS)', '0.9linear_weight', '0.8linear_weight', '0.7linear_weight', '0.6linear_weight', '0.5linear_weight']
    df_grouped['title'] = titles

    return df_grouped

def plot_and_save_all_categories(all_data, output_folder, agg_type):
    """
    Plots each category across all CSV files.
    """
    categories = ['consensus_tps', 'consensus_latency', 'end_to_end_tps', 'end_to_end_latency']

    for category in categories:
        plot_category_across_files(all_data, category, output_folder, agg_type)

# Define the input and output folders
input_folder = 'data/geodec_hotstuff_2'
output_folder_base = 'data/geodec_hotstuff_2/plots'

# Get all CSV files from the input folder
csv_files = get_all_files(input_folder)

# Choose aggregation type ('median' or 'max')
agg_type = 'max'  # Set to 'max' if you want to plot the max values

# List to store data from all CSV files
all_data = []

# Process each CSV file and collect the data
for csv_file in csv_files:
    csv_file_path = os.path.join(input_folder, csv_file)

    # Process the CSV file and get the aggregated data
    df_aggregated = process_csv_file(csv_file_path, agg_type)

    # Append the data and the csv file name to the list
    all_data.append((df_aggregated, csv_file_path))

# Create an output folder if it doesn't exist
if not os.path.exists(output_folder_base):
    os.makedirs(output_folder_base)

# Generate and save the comparison plots for all categories
plot_and_save_all_categories(all_data, output_folder_base, agg_type)