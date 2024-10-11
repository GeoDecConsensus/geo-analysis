import numpy as np
import os
import pandas as pd
import haversine as hs  # Ensure you have the haversine library installed
from numpy.linalg import eig
from utils.normalization import Normalization

def compute_all_distances(df):
    """Compute all distances between nodes and return a distance matrix."""
    n = len(df)
    distance_matrix = np.zeros((n, n))  # Initialize a square matrix for distances

    for i, validator in df.iterrows():
        s_coords = (validator['latitude'], validator['longitude'])
        for j, other_validator in df.iterrows():
            if i != j:
                d_coords = (other_validator['latitude'], other_validator['longitude'])
                distance = hs.haversine(s_coords, d_coords)
                distance_matrix[i, j] = distance  # Store the computed distance
    
    return distance_matrix

def create_weighted_adjacency_matrix(distance_matrix, df, col='stake_weight'):
    """Create a weighted adjacency matrix based on distances and stake weights."""
    df = Normalization.normalize_column(df, col)
    
    # Get the maximum distance for normalization
    max_distance = np.max(distance_matrix)

    # Initialize the weighted adjacency matrix
    n = len(df)
    weighted_adjacency_matrix = np.zeros((n, n))

    # Fill the weighted adjacency matrix
    for i in range(n):
        for j in range(n):
            if i != j:
                stake_weight_i = df.iloc[i][col]
                stake_weight_j = df.iloc[j][col]
                distance = distance_matrix[i, j]
                
                # Calculate d based on the normalized distance
                d = 1 - (distance / max_distance)
                weighted_adjacency_matrix[i, j] = stake_weight_i * stake_weight_j * d
    
    return weighted_adjacency_matrix

def compute_eigenvector_centrality(weighted_adjacency_matrix):
    """Compute the eigenvector centrality from the weighted adjacency matrix."""
    eigenvalues, eigenvectors = eig(weighted_adjacency_matrix)
    max_index = np.argmax(eigenvalues)
    principal_eigenvector = np.real(eigenvectors[:, max_index])
    centrality_scores = principal_eigenvector / np.sum(principal_eigenvector)
    return centrality_scores

def gini_coefficient(values):
    """Calculate the Gini coefficient of a numpy array."""
    if len(values) == 0:
        return 0
    mean = np.mean(values)
    sum_diff = np.sum(np.abs(np.subtract.outer(values, values)))
    return (sum_diff / (2 * len(values)**2 * mean)) if mean != 0 else 0

def get_all_files(folder_path):
    """Returns a list of all CSV files in the specified folder."""
    return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f.endswith('.csv')]

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

# Use get_all_files if you want to process all CSVs in the directory
files = get_all_files('data/wc/')

results_list = []  # List to hold Gini coefficients
centrality_measures = []  # List to hold centrality scores

for file in files:
    df = pd.read_csv(f'data/wc/{file}')
    chain = os.path.splitext(file)[0]
    print(f'Processing {chain}...')
    
    # Prepare a dictionary to hold Gini coefficients for the current file
    gini_values = {'file': chain}  # Start with the filename
    
    # Compute distance matrix
    distance_matrix = compute_all_distances(df)
    
    for col in weight_columns:
        # Generate the weighted adjacency matrix
        weighted_adjacency_matrix = create_weighted_adjacency_matrix(distance_matrix, df, col=col)
        
        # Compute eigenvector centrality
        centrality_scores = compute_eigenvector_centrality(weighted_adjacency_matrix)
        
        # Calculate Gini coefficient
        gini = gini_coefficient(centrality_scores)
        print(f'Eigenvector centrality Gini for {col}: {gini}')
        
        # Store the Gini coefficient in the dictionary
        gini_values[f'{col}'] = gini
        
        # Store centrality measures along with chain name and column
        centrality_measures.append({
            'file': chain,
            'weight_column': col,
            'centrality_scores': centrality_scores.tolist()  # Convert to list for easier saving
        })
    
    # Append the Gini values for the current file to the results list
    results_list.append(gini_values)

# Convert the list of dictionaries to a DataFrame for Gini values
results_df = pd.DataFrame(results_list)

# Save results to a CSV file for Gini coefficients
results_df.to_csv('results/exponential_centrality_measures_wc.csv', index=False)
print('Results saved to exponential_centrality_measures_wc.csv')
