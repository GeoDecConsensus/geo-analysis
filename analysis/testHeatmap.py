import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# WORKS BUT WE DO NOT NEED IT FOR PAPER
# Load the Ethereum data
eth_file_path = 'data/pre_processed_data/ethereum.csv'  # Update with your actual file path
df = pd.read_csv(eth_file_path)

# Group by country and sum the stake weights
country_stakes = df.groupby('country')['stake_weight'].sum().reset_index()

# Calculate total stake for percentage calculation
total_stake = country_stakes['stake_weight'].sum()
country_stakes['stake_percentage'] = (country_stakes['stake_weight'] / total_stake) * 100

# Load the world map data from the shapefile
world = gpd.read_file('ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp')  # Update with the actual path to the shapefile

# Merge with country stakes data
world = world.merge(country_stakes, how='left', left_on='ADMIN', right_on='country')

# Plotting
fig, ax = plt.subplots(1, 1, figsize=(15, 10))
world.boundary.plot(ax=ax, color='black')

# Plot the countries with stake weight
world.plot(column='stake_percentage', ax=ax, legend=True,
           legend_kwds={'label': "Stake Weight Percentage by Country",
                        'orientation': "horizontal"},
           cmap='OrRd', missing_kwds={'color': 'lightgrey'})


plt.title('Stake Weight Distribution by Country for Ethereum')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.tight_layout()
plot_file_path = os.path.join('results/', f'heatmap_ethereum.pdf')  # Save as PDF
plt.savefig(plot_file_path, format='pdf', dpi=300, transparent=True)
plt.close()  # Close the plot to free memory
