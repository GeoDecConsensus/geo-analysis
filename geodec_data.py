import logging

import pandas as pd
from geopy.distance import geodesic

# Output file name
OUTPUT_FILE = "geodec_data/sui/sui_final.csv"

# Setup logging
logging.basicConfig(filename="geodec_data/sui/logs.txt", level=logging.INFO, format="%(asctime)s - %(message)s")


# Function to calculate the distance between two sets of coordinates
def calculate_distance(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).km


# Step 1: Read the CSV files
validator_df = pd.read_csv("data/pre_processed_data/sui.csv")
servers_df = pd.read_csv("geodec_data/servers.csv")


# Step 2: For each validator, find the nearest server
def find_nearest_server(lat, lon, servers_df):
    min_distance = float("inf")
    nearest_server_id = None
    nearest_lat = None
    nearest_lon = None

    for idx, server in servers_df.iterrows():
        server_lat = server["latitude"]
        server_lon = server["longitude"]
        distance = calculate_distance(lat, lon, server_lat, server_lon)

        if distance < min_distance:
            min_distance = distance
            nearest_server_id = server["id"]
            nearest_lat = server_lat
            nearest_lon = server_lon

    return nearest_server_id, nearest_lat, nearest_lon, min_distance


# Step 3: Create a new dataframe for the merged results and track distances
merged_data = []
distances = []
total_validators = 0

for idx, validator in validator_df.iterrows():
    lat = validator["latitude"]
    lon = validator["longitude"]
    stake_weight = validator["stake_weight"]
    total_validators += 1

    nearest_server_id, nearest_lat, nearest_lon, distance = find_nearest_server(lat, lon, servers_df)

    # Log the distance to check accuracy
    logging.info(f"Validator {validator['uuid']} merged with server {nearest_server_id} at distance {distance:.2f} km.")
    distances.append(distance)

    # Append the data to the merged list
    merged_data.append(
        {
            "uuid": validator["uuid"],
            "stake_weight": stake_weight,
            "server_id": nearest_server_id,
            "server_latitude": nearest_lat,
            "server_longitude": nearest_lon,
            "distance_km": distance,
        }
    )

# Step 4: Aggregate stake weights and group by server location
merged_df = pd.DataFrame(merged_data)

# Log distance statistics (range, max)
max_distance = max(distances)
min_distance = min(distances)
average_distance = sum(distances) / len(distances)

logging.info(
    f"Max distance: {max_distance:.2f} km, Min distance: {min_distance:.2f} km, Average distance: {average_distance:.2f} km"
)

# Step 5: Sum the stake weights for merged validators with the same server
aggregated_df = merged_df.groupby(["server_id", "server_latitude", "server_longitude"], as_index=False).agg(
    {
        "stake_weight": "sum",
        "uuid": lambda x: ",".join(x),  # Combine the UUIDs that were merged
        "distance_km": "mean",  # Average the distances for logging purposes
    }
)

# Log the number of validators after the initial merge
logging.info(f"Number of validators after initial merge: {len(aggregated_df)}")

# Step 6: Check if the number of validators is <= 64
if len(aggregated_df) <= 64:
    logging.info(f"Number of validators is acceptable: {len(aggregated_df)}. No further merging needed.")
else:
    # Step 7: If more than 64 validators, merge the closest ones again
    logging.info(f"Number of validators is greater than 64. Starting second round of merging.")

    while len(aggregated_df) > 64:
        # For each server location, find the closest pair and merge them
        min_distance = float("inf")
        merge_pair = None

        # Find the closest pair of servers to merge
        for i, loc1 in aggregated_df.iterrows():
            for j, loc2 in aggregated_df.iterrows():
                if i >= j:
                    continue

                distance = calculate_distance(
                    loc1["server_latitude"], loc1["server_longitude"], loc2["server_latitude"], loc2["server_longitude"]
                )

                if distance < min_distance:
                    min_distance = distance
                    merge_pair = (i, j)

        # Merge the closest pair
        if merge_pair:
            i, j = merge_pair
            aggregated_df.at[i, "stake_weight"] += aggregated_df.at[j, "stake_weight"]
            aggregated_df.at[i, "uuid"] += "," + aggregated_df.at[j, "uuid"]
            aggregated_df = aggregated_df.drop(j).reset_index(drop=True)

            logging.info(f"Merged validators at index {i} and {j}, with distance {min_distance:.2f} km.")
            logging.info(f"New validator count after merge: {len(aggregated_df)}")

# Step 8: Save the final result to a new CSV file
aggregated_df.to_csv(OUTPUT_FILE, index=False)

logging.info("Merging and aggregation complete. Output saved to 'merged_validators_final.csv'.")
print(
    f"Merging and aggregation complete. Check 'merged_validators_final.csv'. Number of validators: {len(aggregated_df)}"
)
