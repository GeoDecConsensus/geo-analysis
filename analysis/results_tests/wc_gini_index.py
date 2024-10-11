import numpy as np
import os
import pandas as pd
import haversine as hs

# from weight_computation import WeightComputation
def get_all_files(folder_path):
    """
    This function returns a list of all files in the given folder path.
    
    :param folder_path: Path to the folder
    :return: List of files in the folder
    """
    # Get a list of all files in the folder
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f.endswith('.csv')]
    return files

def gini_coefficient(values):
    """Calculate the Gini coefficient of a numpy array."""
    if len(values) == 0:
        return 0
    values = normalize(values)
    # Mean absolute difference
    mean = np.mean(values)
    sum_diff = np.sum(np.abs(np.subtract.outer(values, values)))  # Outer subtraction for all combinations
    return (sum_diff / (2 * len(values)**2 * mean)) if mean != 0 else 0

def normalize(values):
    """Normalize the values to the range [0, 1]."""
    min_val = np.min(values)
    max_val = np.max(values)
    return (values - min_val) / (max_val - min_val) if max_val > min_val else values

# Example usage for regional grouping
def calculate_gini_by_region(df, region_col='country', stake_col='stake_weight'):
    """Calculate Gini index for stake weights grouped by region."""
    grouped = df.groupby(region_col)[stake_col].sum()
    return gini_coefficient(grouped.values)

def calculate_distance_based_gini(df, distance_threshold, stake_col='stake_weight'):
    """Calculate the distance-based Gini index for stake weights within a given distance threshold."""
    gini_values = []
    zero_count = 0  # Counter for zero Gini values
    
    stake_weights = df[stake_col].to_numpy()
    aggregated_stakes = []  # List to hold aggregated stakes
    
    # Create a distance matrix
    for idx, validator in df.iterrows():
        # Extract the latitude and longitude of the current validator
        s_coords = (validator['latitude'], validator['longitude'])
        
        # Calculate distances to all other validators
        distances = np.array([hs.haversine(s_coords, (row['latitude'], row['longitude'])) for _, row in df.iterrows()])
        
        # Find neighbors within the specified distance threshold
        neighbors_idx = np.where(distances <= distance_threshold)[0]
        
        # Compute aggregated stake weights for neighbors
        if len(neighbors_idx) > 1:
            aggregated_stake = stake_weights[neighbors_idx].sum()  # Include own stake
            aggregated_stakes.append(aggregated_stake)
        else:
            aggregated_stakes.append(stake_weights[idx])  # Own stake if no neighbors
            zero_count += 1  # Increment the counter for zero Gini values
    
    df['aggregated_stake'] = aggregated_stakes  # Add aggregated stake as a new column
    overall_gini = gini_coefficient(aggregated_stakes)  # Calculate Gini for all aggregated stakes

    print(f"Total number of zero Neighbours values: {zero_count}")  # Print the count of zero Gini values
    return overall_gini  # Return mean Gini and overall Gini


# Use get_all_files if you want to process all CSVs in the directory
files = get_all_files('data/wc/')

results_list = []  # List to hold results

weight_columns = [
    'stake_weight', 
    '0.9exponential_weight', 
    '0.8exponential_weight',
    '0.7exponential_weight', 
    '0.6exponential_weight', 
    '0.5exponential_weight',
    '0.9linear_weight', 
    '0.8linear_weight', 
    '0.7linear_weight', 
    '0.6linear_weight', 
    '0.5linear_weight'
]

for file in files:
    df = pd.read_csv(f'data/wc/{file}')
    chain = os.path.splitext(file)[0]
    print(f'Processing {chain}...')
    
    # Prepare a dictionary to hold Gini coefficients for the current file
    gini_values = {'file': chain}  # Start with the filename
    
    for col in weight_columns:
        
        # Calculate Gini coefficient
        gini = calculate_gini_by_region(df,stake_col=col)
        print(f'Gini for {col}: {gini}')
        
        # Store the Gini coefficient in the dictionary
        gini_values[f'{col}'] = gini
    
    # Append the Gini values for the current file to the results list
    results_list.append(gini_values)

# Convert the list of dictionaries to a DataFrame
results_df = pd.DataFrame(results_list)

# Save results to a CSV file
results_df.to_csv('results/gini_wc.csv', index=False)
print('Results saved to gini_wc.csv')