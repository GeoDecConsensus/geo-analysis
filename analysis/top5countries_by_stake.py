import matplotlib.pyplot as plt
import os
import pandas as pd

# Enable LaTeX and set fonts for better formatting
plt.rcParams['text.usetex'] = True
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']  # LNCS compatible font
plt.rcParams['axes.titlesize'] = 12  # Title size
plt.rcParams['axes.labelsize'] = 10  # Axis labels size
plt.rcParams['xtick.labelsize'] = 8  # X-tick size
plt.rcParams['ytick.labelsize'] = 8  # Y-tick size
plt.rcParams['legend.fontsize'] = 10  # Legend font size
plt.rcParams['figure.titlesize'] = 12  # Figure title size

def get_all_files(folder_path):
    """
    This function returns a list of all files in the given folder path.
    
    :param folder_path: Path to the folder
    :return: List of files in the folder
    """
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f.endswith('.csv')]
    return files

input_folder = 'data/pre_processed_data/'
files = get_all_files(input_folder)
latex_tables = []

for file in files:
    df = pd.read_csv(input_folder + file)
    blockchain_name = file.replace('.csv', '')

    total_stake_system = df['stake_weight'].sum()
    grouped_df = df.groupby('country')['stake_weight'].sum().reset_index()
    top_countries = grouped_df.nlargest(8, 'stake_weight')
    top_countries['stake_percentage'] = (top_countries['stake_weight'] / total_stake_system) * 100

    # Create LaTeX table with caption
    latex_table = f"""
\\begin{{table}}[htbp]
    \\centering
    \\caption{{Top 8 Countries by Stake Percentage for {blockchain_name}}}
    \\begin{{tabular}}{{|l|c|}}
    \\hline
    Country & Stake Percentage \\\\
    \\hline
    """
    
    for _, row in top_countries.iterrows():
        latex_table += f"{row['country']} & {row['stake_percentage']:.2f} \\\\\n"
    
    latex_table += "\\hline\n\\end{tabular}\n\\end{table}\n"
    latex_tables.append(latex_table)

# Save all tables in one .tex file
with open('results/all_top8_countries_output.tex', 'w') as f:
    f.write("\\documentclass{article}\n")
    f.write("\\usepackage{booktabs}\n")
    f.write("\\usepackage{caption}\n")
    f.write("\\begin{document}\n")
    f.write("\\appendix\n")  # Start appendix

    for table in latex_tables:
        f.write(table)

    f.write("\\end{document}\n")
    # # Assuming top_countries DataFrame has been prepared with columns 'country' and 'stake_weight'
    ### USED FOR PLOT IN PAPER --- WORKS
    # if file=='ethereum.csv':
    #     plt.figure(figsize=(10, 6))
    #     bars = plt.bar(top_countries['country'], top_countries['stake_percentage'], color='lightcoral')
    #     plt.xlabel(r'\textbf{Country}', fontsize=24)
    #     plt.ylabel(r'\textbf{Total Stake Percentage}', fontsize=24)
    #     plt.title(r'\textbf{Top 5 Countries By Stake Ethereum}', fontsize=36)
         
    #     # Add labels inside each bar
    #     for bar in bars:
    #         yval = bar.get_height()
    #         plt.text(bar.get_x() + bar.get_width()/2, yval - 0.01, f'{yval:.2f}', ha='center', va='top', fontsize=32, color='black')


    #     plt.xticks(fontsize=22)
    #     plt.yticks(fontsize=24) 
    #     plt.tight_layout()
    #     plot_file_path = os.path.join('results/', f'top5_Ethereum_histogram.pdf')  # Save as PDF
    #     plt.savefig(plot_file_path, format='pdf', dpi=300, transparent=True)
    #     plt.close()  # Close the plot to free memory

