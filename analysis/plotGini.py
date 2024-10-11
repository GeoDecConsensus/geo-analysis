import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors

# Read the data from the CSV file
df = pd.read_csv('results/gini_wc.csv')

# Sort the DataFrame alphabetically by the 'file' column
df = df.sort_values(by='file')

# Define the chains and the weights to plot
chains = df['file']
weights = ['stake_weight', '0.9linear_weight', '0.8linear_weight', '0.7linear_weight', '0.6linear_weight', '0.5linear_weight']
weight_labels = ['PoS', 'Lambda = 0.9', 'Lambda = 0.8', 'Lambda = 0.7', 'Lambda = 0.6', 'Lambda = 0.5']

# Set up the bar plot
x = np.arange(len(chains))  # Label locations
width = 0.12  # Width of each bar

# Define color shades within lightcoral for the bars
base_color = mcolors.to_rgba('lightcoral')
colors = [mcolors.to_rgba(base_color, alpha=1 - i*0.15) for i in range(len(weights))]

fig, ax = plt.subplots(figsize=(12, 8))

# Plot each weight's Gini coefficient as a bar
for i, (weight, label, color) in enumerate(zip(weights, weight_labels, colors)):
    ax.bar(x + i * width, df[weight], width, label=label, color=color)

# Add labels and title
ax.set_xlabel('Blockchain')
ax.set_ylabel('Gini Coefficient')
ax.set_title('Gini Coefficient Comparison Across Chains for PoS and GPoS (Varying Lambda)')
ax.set_xticks(x + width * 2.5)  # Adjust x-ticks to center
ax.set_xticklabels(chains)
ax.legend(title='Weight Type')

# Show grid and tight layout
plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
plt.tight_layout()

# Show the plot
plt.show()
