import numpy as np
import os
import pandas as pd
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt
import geopandas as gpd

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

def compute_kde(df, lat_col='latitude', lon_col='longitude', weight_col='stake_weight'):
    """Calculate Kernel Density Estimation (KDE) using stake weight as weights."""
    df[weight_col] = df[weight_col]/df[weight_col].sum()
    xy = np.vstack([df[lon_col], df[lat_col]])
    kde = gaussian_kde(xy, weights=df[weight_col])
    return kde

def get_all_files(folder_path):
    """Get a list of all CSV files in the given folder."""
    return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f.endswith('.csv')]

def plot_kde_with_map(df, chain, output_folder='results', show_boundaries=True):
    """Plot the KDE of stake weights with optional world boundaries and save the plot."""
    # Compute KDE
    kde = compute_kde(df)
    
    # Create a grid to evaluate KDE
    xgrid = np.linspace(df['longitude'].min(), df['longitude'].max(), 100)
    ygrid = np.linspace(df['latitude'].min(), df['latitude'].max(), 100)
    xgrid, ygrid = np.meshgrid(xgrid, ygrid)
    positions = np.vstack([xgrid.ravel(), ygrid.ravel()])
    density = kde(positions).reshape(xgrid.shape)

    # Load the world map
    world = gpd.read_file('ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp')  # Adjust this path

    # Create output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Plot the density with a map background
    plt.figure(figsize=(10, 6))
    ax = plt.gca()
    
    if show_boundaries:
        world.boundary.plot(ax=ax, color='black')  # Draw world boundaries
    
    contour = plt.contourf(xgrid, ygrid, density, levels=20, cmap='Reds', vmin=0, vmax=0.0002)
    plt.colorbar(contour, ax=ax, shrink=0.4, label=r'\textbf{Density of Stake Weight}', ticks=[0, 0.00005, 0.0001, 0.00015, 0.0002])

    plt.title(r'\textbf{KDE of Stake Weight Distribution - ' + chain.capitalize() + '}', fontsize=12)
    plt.xlabel(r'\textbf{Longitude}', fontsize=10)
    plt.ylabel(r'\textbf{Latitude}', fontsize=10)

    # Set the limits to the data range
    plt.xlim(df['longitude'].min(), df['longitude'].max())
    plt.ylim(df['latitude'].min(), df['latitude'].max())

    # Save the plot
    plot_file_path = os.path.join(output_folder, f'{chain}_kde_plot.pdf')  # Save as PDF
    plt.savefig(plot_file_path, format='pdf', dpi=300, transparent=True)
    plt.close()  # Close the plot to free memory

    print(f'Saved plot to {plot_file_path}')

def analyze_files(folder, output_folder='results', show_boundaries=True):
    """Analyze all CSV files in a specified folder."""
    files = get_all_files(folder)  # Get all CSV files

    for file in files:
        df = pd.read_csv(os.path.join(folder, file))
        plot_kde_with_map(df, file.replace(".csv", ""), output_folder, show_boundaries)

# Example usage
if __name__ == "__main__":
    folder = 'data/pre_processed_data/'  # Adjust as necessary
    analyze_files(folder, output_folder='results/KDE/', show_boundaries=True)  # Set to False to hide boundaries
