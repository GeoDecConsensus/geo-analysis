import numpy as np
import os
import pandas as pd
import haversine as hs
from numpy.linalg import eig
import matplotlib.pyplot as plt  # Import matplotlib for plotting
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

def get_all_files(folder_path):
    """Returns a list of all CSV files in the specified folder."""
    return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f.endswith('.csv')]

# Use get_all_files to process all CSVs in the directory
files = get_all_files('data/wc/')

centrality_scores_list = []  # List to hold centrality scores for box plot
file_labels = []  # To store names of the files for labeling in the plot

for file in files:
    df = pd.read_csv(f'data/wc/{file}')
    chain = os.path.splitext(file)[0]
    print(f'Processing {chain}...')
    
    distance_matrix = compute_all_distances(df)
    col = 'stake_weight'
        
    # Generate the weighted adjacency matrix
    weighted_adjacency_matrix = create_weighted_adjacency_matrix(distance_matrix, df, col=col)
        
    # Compute eigenvector centrality
    centrality_scores = compute_eigenvector_centrality(weighted_adjacency_matrix)
    
    # Store the centrality scores for box plotting
    centrality_scores_list.append(centrality_scores)
    file_labels.append(chain)  # Store the name of the file for labeling

np.save('results/centrality_scores.npy', np.array(centrality_scores_list, dtype=object))
