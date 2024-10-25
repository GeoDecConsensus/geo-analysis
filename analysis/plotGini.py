import os

import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams.update(plt.rcParamsDefault)
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

# Load the CSV file containing Gini coefficients
file_path = 'results/gini.csv'  # Update this with your actual file path
df = pd.read_csv(file_path)

# Clean up the blockchain names
df['blockchain'] = df['blockchain'].str.replace('.csv', '', regex=False).str.title()  # Remove .csv and capitalize first letter
df['blockchain'] = df['blockchain'].replace('Ethernodes', 'Ethereum Nodes')  # Replace with proper naming

# Sort the DataFrame by blockchain names
df.sort_values(by='blockchain', inplace=True)

# Create a bar chart of Gini coefficients for all blockchains
plt.figure(figsize=(10, 6))
bars = plt.bar(df['blockchain'], df['gini'], color='lightcoral')  # Calmer color

# Adding Gini values inside each bar with increased font size
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval - 0.05, round(yval, 2), ha='center', va='top', color='black', fontsize=36)

plt.xlabel(r'\textbf{Blockchain}', fontsize=24)
plt.ylabel(r'\textbf{Gini Coefficient}', fontsize=24)
plt.title(r'\textbf{Geospatial Gini Coefficients- Country}', fontsize=36)
plt.xticks(fontsize=18)  # Rotate labels for better readability
plt.yticks(fontsize=24)
plt.tight_layout()
# Save the plot
plot_file_path = os.path.join('results/', f'gini_hitsogram.pdf')  # Save as PDF
plt.savefig(plot_file_path, format='pdf', dpi=300, transparent=True)
plt.close()  # Close the plot to free memory
