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

# Example usage
files = get_all_files('data/pre_processed_data/')
# files = ['aptos.csv']
results_list = []

for file in files:
    df = pd.read_csv('data/pre_processed_data/' + file)
    
    # weightComputation = WeightComputation(df)
    # df = weightComputation.get_updated_df()


    # Get the length of the dataframe
    rows_count = len(df)
    
#     # Dictionary to store the Gini results
    file_results = {
        'blockchain': file,
        'rows': rows_count,
    }
    
    file_results[f'gini'] = calculate_gini_by_region(df)
    
    # Calculate Distance-based Gini for 100 km
    gini_for_100km = calculate_distance_based_gini(df, 100)
    file_results['gini_100'] = gini_for_100km
    
    # Calculate Distance-based Gini for 200 km
    gini_for_200km = calculate_distance_based_gini(df, 200)
    file_results['gini_200'] = gini_for_200km
    
    # Calculate Distance-based Gini for 600 km
    gini_for_400km = calculate_distance_based_gini(df, 400)
    file_results['gini_400'] = gini_for_400km
    
    # Calculate Distance-based Gini for 500 km
    gini_for_500km = calculate_distance_based_gini(df, 500)
    file_results['gini_500'] = gini_for_500km
    
    # Calculate Distance-based Gini for 600 km
    gini_for_600km = calculate_distance_based_gini(df, 600)
    file_results['gini_600'] = gini_for_600km
    
    # Calculate Distance-based Gini for 800 km
    gini_for_800km = calculate_distance_based_gini(df, 800)
    file_results['gini_800'] = gini_for_800km
    
    # Calculate Distance-based Gini for 1000 km
    gini_for_1000km = calculate_distance_based_gini(df, 1000)
    file_results['gini_1000'] = gini_for_1000km
    
    # Calculate Distance-based Gini for 1500 km
    gini_for_1500km = calculate_distance_based_gini(df, 1500)
    file_results['gini_1500'] = gini_for_1500km
    
    # Calculate Distance-based Gini for 2000 km
    gini_for_2000km = calculate_distance_based_gini(df, 2000)
    file_results['gini_2000'] = gini_for_2000km
    
    # Append the result to the list
    results_list.append(file_results)

# Convert the list of dictionaries to a pandas DataFrame
results_df = pd.DataFrame(results_list)
print(results_df)

# Save the DataFrame to a CSV file
results_df.to_csv('results/gini.csv', index=False)