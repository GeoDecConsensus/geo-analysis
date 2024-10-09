import numpy as np
import matplotlib.pyplot as plt
import os

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

# Load the centrality scores
loaded_centrality_scores_list = np.load('results/centrality_scores.npy', allow_pickle=True)

# Define the blockchain names for labeling
chains = ['Sui', 'Ethereum Nodes', 'Solana', 'Aptos', 'Ethereum', 'Avalanche']

# Sort the chains and get the sorted indices
sorted_indices = sorted(range(len(chains)), key=lambda k: chains[k])
sorted_chains = [chains[i] for i in sorted_indices]
sorted_scores = [loaded_centrality_scores_list[i] for i in sorted_indices]

# Define Gini values for each blockchain (replace with actual calculated values)
gini_values = [0.475, 0.421, 0.369, 0.325, 0.298, 0.300]  # Example values

# Define a lighter to darker coral color palette
colors = ['#f08080', '#ef5350', '#f44336', '#e57373', '#c62828', '#d32f2f']  # Different shades of coral
sorted_colors = [colors[i] for i in sorted_indices]

# Create a box plot for the centrality scores
plt.figure(figsize=(14, 7))

# Create the box plot
box = plt.boxplot(sorted_scores, labels=sorted_chains, 
                  widths=0.5,  # Increase the width of the boxes
                  boxprops=dict(alpha=0.0),  # Make the box outline invisible initially
                  medianprops={'color': '#800080', 'linewidth': 2},  # Median line color and thickness
                  whiskerprops={'color': '#ff7f0e', 'linewidth': 2},  # Whisker color and thickness
                  capprops={'color': '#ff7f0e', 'linewidth': 2},  # Cap color and thickness
                  flierprops={'marker': 'o', 'color': 'red', 'alpha': 0.5, 'markersize': 8}  # Outlier marker
                 )

# Loop through each box to apply individual colors and filling with hatch patterns
for i, box_patch in enumerate(box['boxes']):
    # Create a rectangle patch
    box_rect = plt.Rectangle((box_patch.get_xdata()[0], box_patch.get_ydata()[1]),  # x, y position
                             box_patch.get_xdata()[1] - box_patch.get_xdata()[0],  # width
                             box_patch.get_ydata()[2] - box_patch.get_ydata()[1],  # height
                             color=sorted_colors[i],  # Set the color
                             alpha=0.7,  # Set transparency
                             hatch='/',  # Set hatch pattern
                             edgecolor='black')  # Set edgae color

    # Add the rectangle patch to the plot
    plt.gca().add_patch(box_rect)

# Calculate mean and add it to the plot for each box
for i in range(len(sorted_scores)):
    mean_centrality = np.mean(sorted_scores[i])
    plt.scatter([i + 1], [mean_centrality], color='green', label='Mean' if i == 0 else "", zorder=5, s=100)
    median_centrality = np.median(sorted_scores[i])
    plt.scatter([i + 1], [median_centrality], color='red', label='Median' if i == 0 else "", zorder=5, s=100)

    # Display Gini value below the corresponding box
    plt.text(i + 1, -0.1 * np.max(sorted_scores[i]), f'G = {gini_values[i]:.3f}', 
             fontsize=10, ha='center', color='black')

# Adding titles and labels with larger font sizes
# plt.xlabel('Blockchains', fontsize=20)
plt.ylabel('Eigenvector Centrality Scores (Log Scale)', fontsize=24)

# Set logarithmic scale
plt.yscale('log')  

plt.grid(axis='y', linestyle='--', alpha=0.7)

# Improve readability by rotating x-axis labels and increasing font size
plt.xticks(fontsize=20)
plt.yticks(fontsize=24)

# Show legend
plt.legend(fontsize=20)

# Save the plot
plot_file_path = os.path.join('results/', f'centrality_boxplots.pdf')  # Save as PDF
plt.savefig(plot_file_path, format='pdf', dpi=300, transparent=True)
plt.close()  # Close the plot to free memory
