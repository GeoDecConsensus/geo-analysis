import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Enable LaTeX and set fonts for better formatting
plt.rcParams['text.usetex'] = True
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']  # LNCS compatible font
plt.rcParams['axes.titlesize'] = 12  # Title size
plt.rcParams['axes.labelsize'] = 10  # Axis labels size
plt.rcParams['xtick.labelsize'] = 20  # X-tick size
plt.rcParams['ytick.labelsize'] = 20  # Y-tick size
plt.rcParams['legend.fontsize'] = 10  # Legend font size
plt.rcParams['figure.titlesize'] = 12  # Figure title size

# Read the data from the CSV file
df = pd.read_csv('results/centrality_measures_wc.csv')

# Sort the DataFrame alphabetically by the 'file' column
df = df.sort_values(by='file')

# Define the chains and the weights to plot
chains = df['file'].str.capitalize().replace({'ethernodes': 'Ethereum Nodes'})  # Capitalize and replace
weights = ['stake_weight', '0.9linear_weight', '0.8linear_weight', '0.7linear_weight', '0.6linear_weight', '0.5linear_weight']

# Set up the bar plot
x = np.arange(len(chains))  # Label locations
width = 0.12  # Width of each bar

fig, ax = plt.subplots(figsize=(12, 8))

# Define a more professional, muted color palette
colors = ['#4E79A7', '#F28E2B', '#59A14F', '#EDC948', '#B07AA1', '#76B7B2']

# Map each weight to the corresponding label with the lambda symbol
weight_labels = {
    'stake_weight': r'$\lambda = 1 (PoS)$',
    '0.9linear_weight': r'$\lambda = 0.9$',
    '0.8linear_weight': r'$\lambda = 0.8$',
    '0.7linear_weight': r'$\lambda = 0.7$',
    '0.6linear_weight': r'$\lambda = 0.6$',
    '0.5linear_weight': r'$\lambda = 0.5$'
}

# Plot each weight's Gini coefficient as a bar with distinct muted colors
for i, weight in enumerate(weights):
    ax.bar(x + i * width, df[weight], width, label=weight_labels[weight], color=colors[i])

# Add labels and title
ax.set_ylabel('Gini Coefficient of Eigenvector Centrality Scores', fontsize=20)  # Set Y-label fontsize to 20
ax.set_xticks(x + width * 2.5)  # Adjust x-ticks to center
ax.set_xticklabels(chains, fontsize=20)

# Set Y-ticks font size
plt.yticks(fontsize=20)

# Place legend inside the plot area
ax.legend(title='Configuration', loc='upper right', fontsize=20, title_fontsize=24)

# Plot trendlines for each chain to show the evolution of Gini coefficients across lambda values
for i, chain in enumerate(chains):
    # Extract Gini values for this chain
    gini_values = df.loc[df['file'] == chain.lower(), weights].values.flatten()  # Use lower case for matching
    
    # Calculate x-coordinates for trendlines (centered across the bars for this chain)
    trendline_x = x[i] + np.linspace(0, width * (len(weights) - 1), len(weights))
    
    # Fit a line (linear regression) to show trend and plot it
    z = np.polyfit(trendline_x, gini_values, 1)
    p = np.poly1d(z)
    ax.plot(trendline_x, p(trendline_x), linestyle='--', color='grey', linewidth=1, alpha=0.7)

# Show grid and tight layout
plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
plt.tight_layout()


# Save the plot
plot_file_path = os.path.join('results/', f'centrality_measures_wc_gini.pdf')  # Save as PDF
plt.savefig(plot_file_path, format='pdf', dpi=300, transparent=True)
plt.close()  # Close the plot to free memory