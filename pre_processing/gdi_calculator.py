import pandas as pd
import math
import haversine as hs  # Install using: pip install haversine

class GDI_Calculator:
    def __init__(self, df, logger=None):
        """
        Initialize the GDI_Calculator class with a pandas DataFrame and a logger.
        
        :param df: A pandas DataFrame with 'uuid', 'latitude', 'longitude', and 'stake_weight'.
        :param logger: Logger function to handle logging instead of print.
        """
        self.df = df
        self.dist_matrix = self._getDistanceMatrix()
        self.logger = logger if logger else print  # Default to print if no logger provided

    def _getDistanceMatrix(self):
        """
        Calculates the distance matrix between servers using the Haversine formula.
        
        :return: A pandas DataFrame representing the distance matrix between all servers.
        """
        dist = pd.DataFrame(columns=self.df["uuid"], index=self.df["uuid"])

        for source in self.df.index:
            s_uuid = self.df["uuid"][source]
            s_coords = (self.df['latitude'][source], self.df['longitude'][source])
            for destination in self.df.index:
                d_uuid = self.df["uuid"][destination]
                d_coords = (self.df['latitude'][destination], self.df['longitude'][destination])
                # Calculate distance using Haversine formula
                dist.at[s_uuid, d_uuid] = hs.haversine(s_coords, d_coords) 
        return dist

    def merge_closest_validators(self, threshold_distance=20):
        """
        Cleans the dataset by merging validators that are within a threshold distance of each other.
        Precompute all pairs below the threshold, then merge them.
        
        :param threshold_distance: The distance threshold (in km) for merging validators.
        :return: A cleaned pandas DataFrame.
        """
        # Step 1: Precompute all pairs below the threshold distance
        dist_matrix = self.dist_matrix
        merge_pairs = []
        
        for source_uuid in dist_matrix.columns:
            for destination_uuid in dist_matrix.index:
                if source_uuid != destination_uuid and dist_matrix.at[source_uuid, destination_uuid] < threshold_distance:
                    merge_pairs.append((source_uuid, destination_uuid, dist_matrix.at[source_uuid, destination_uuid]))

        # Sort pairs by distance to prioritize merging closer pairs
        merge_pairs.sort(key=lambda x: x[2])  # Sort by the distance (3rd element in tuple)

        # Step 2: Perform the merging
        merged_uuids = set()
        
        for source_uuid, destination_uuid, dist in merge_pairs:
            if destination_uuid not in merged_uuids and source_uuid not in merged_uuids:
                # Check if the destination UUID still exists in the dataframe before accessing it
                if not self.df[self.df['uuid'] == destination_uuid].empty:
                    # Merge stake_weight
                    self.df.loc[self.df['uuid'] == source_uuid, 'stake_weight'] += self.df.loc[self.df['uuid'] == destination_uuid, 'stake_weight'].values[0]

                    # Mark destination UUID for removal
                    merged_uuids.add(destination_uuid)

        # Step 3: Drop merged UUIDs from the dataframe and dist_matrix
        self.df = self.df[~self.df['uuid'].isin(merged_uuids)]
        dist_matrix.drop(index=merged_uuids, columns=merged_uuids, inplace=True)

        # Log the final number of rows in the DataFrame
        self.logger(f"No. of rows post close proximity merge, under {threshold_distance}km: {len(self.df)}")
        return self.df

    def calculate_GDI(self):
        """
        Calculates the GeoSpatial Diversity Index (GDI) for the servers based on their pairwise distances
        and the closest nodes that form two-thirds of the total stake weight, and directly updates self.df.
        
        The GDI metric is added as a new column 'GDI' in self.df.
        """
        # Get the distance matrix
        dist_matrix = self.dist_matrix
        
        # Calculate the total stake weight
        total_weight = self.df['stake_weight'].sum()

        # Define the two-third weight threshold
        two_third_weight_threshold = total_weight * (2 / 3)

        # Initialize the 'GDI' column in the DataFrame
        self.df = self.df.copy()
        self.df.loc[:, 'GDI'] = 0.0

        # Loop through each server and calculate the GDI metric
        for uuid in self.df['uuid']:
            # Get the stake weight of each server in the distance matrix
            server_weights = self.df.set_index('uuid')['stake_weight']
            
            total_weight_accumulated = 0
            two_third_sum = 0

            # Sort the distances to ensure calculations from the closest servers
            sorted_distances = sorted(dist_matrix[uuid].items(), key=lambda x: x[1])

            for dest_uuid, dist in sorted_distances:
                # Accumulate the stake weight until the two-thirds threshold is reached
                total_weight_accumulated += server_weights[dest_uuid]
                two_third_sum += dist
                
                if total_weight_accumulated >= two_third_weight_threshold:
                    break

            # Directly update the 'GDI' column for the current uuid
            self.df.loc[self.df['uuid'] == uuid, 'GDI'] = two_third_sum

        # Log the final DataFrame with GDI calculated
        self.logger(f"GDI calculation completed. DataFrame size: {len(self.df)} rows")
        return self.df
