import logging
import os
import uuid

import haversine as hs  # Install using: pip install haversine
import pandas as pd


class ValidatorMerger:
    def __init__(self, validators_df, servers_df, server_threshold=500, logger=None):
        """
        Initialize the ValidatorMerger class with validators and servers DataFrames.

        :param validators_df: DataFrame containing validators with 'uuid', 'latitude', 'longitude', 'stake_weight'.
        :param servers_df: DataFrame containing servers with 'id', 'latitude', 'longitude'.
        :param server_threshold: Maximum allowed distance (in km) between a validator and a server.
        :param logger: Logger function to handle logging instead of print.
        """
        self.validators_df = validators_df.reset_index(drop=True)
        self.servers_df = servers_df.reset_index(drop=True)
        self.server_threshold = server_threshold
        self.logger = logger if logger else print  # Default to print if no logger provided
        # self.mapping_log = []
        self.distance_log = []

    def map_validators_to_servers(self):
        """
        Maps each validator to the nearest server location using the Haversine formula.
        Validators exceeding the server_threshold distance are logged.
        """
        mapped_validators = []
        for idx, validator in self.validators_df.iterrows():
            v_uuid = validator["uuid"]
            v_coords = (validator["latitude"], validator["longitude"])
            min_distance = float("inf")
            nearest_server_id = None
            nearest_server_coords = None

            # Find the nearest server
            for _, server in self.servers_df.iterrows():
                s_id = server["id"]
                s_coords = (server["latitude"], server["longitude"])
                distance = hs.haversine(v_coords, s_coords)

                if distance < min_distance:
                    min_distance = distance
                    nearest_server_id = s_id
                    nearest_server_coords = s_coords

            # Log if distance exceeds threshold
            if min_distance > self.server_threshold:
                self.logger(f"Validator {v_uuid} exceeds server threshold with distance {min_distance:.2f} km.")
                # self.mapping_log.append(
                #     f"Validator {v_uuid} exceeds server threshold with distance {min_distance:.2f} km."
                # )

            # Append mapping information
            mapped_validators.append(
                {
                    "uuid": v_uuid,
                    "stake_weight": validator["stake_weight"],
                    "id": nearest_server_id,
                    "latitude": nearest_server_coords[0],
                    "longitude": nearest_server_coords[1],
                    "distance_km": min_distance,
                }
            )

            # Log distance
            self.distance_log.append(min_distance)
            # self.logger(f"Validator: {v_uuid} Server mapped: {nearest_server_id} Distance {min_distance:.2f} km.")

        # Create a DataFrame of mapped validators
        self.mapped_df = pd.DataFrame(mapped_validators)

        # Log the number of validators exceeding the threshold
        threshold_exceeded = sum(1 for dist in self.distance_log if dist > self.server_threshold)
        self.logger(f"Validators exceeding threshold: {threshold_exceeded}")

    def aggregate_stake_weights(self):
        """
        Aggregates stake weights for validators mapped to the same server.
        """
        self.aggregated_df = self.mapped_df.groupby(["id", "latitude", "longitude"], as_index=False).agg(
            {
                "stake_weight": "sum",
                "uuid": lambda x: ",".join(x),
                "distance_km": "mean",  # Average distance for logging purposes
            }
        )

        # New uuid for each aggregated server
        self.aggregated_df["uuid"] = [str(uuid.uuid4()) for _ in range(len(self.aggregated_df))]

        self.logger(f"Total validators after initial aggregation: {len(self.aggregated_df)}")

    def merge_validators_incrementally(self, target_count=64, initial_threshold=200, increment=100):
        """
        Merges validators incrementally based on proximity until the total count is less than or equal to target_count.

        :param target_count: Desired maximum number of validators after merging.
        :param initial_threshold: Starting distance threshold for merging (in km).
        :param increment: Distance increment to apply if merging doesn't reduce count below target.
        """
        threshold = initial_threshold
        while len(self.aggregated_df) > target_count:
            self.logger(
                f"Current validator count: {len(self.aggregated_df)}. Trying to merge with threshold: {threshold} km."
            )
            self._merge_validators_within_threshold(threshold)
            threshold += increment

    def _merge_validators_within_threshold(self, threshold):
        """
        Merges validators that are within a specified distance threshold.

        :param threshold: Distance threshold (in km) for merging validators.
        """
        merged = False
        dist_matrix = self._get_distance_matrix(self.aggregated_df)

        # Find pairs within threshold
        pairs_to_merge = []
        for idx1 in range(len(dist_matrix)):
            for idx2 in range(idx1 + 1, len(dist_matrix)):
                distance = dist_matrix.iloc[idx1, idx2]
                if distance <= threshold:
                    pairs_to_merge.append((idx1, idx2, distance))

        if not pairs_to_merge:
            self.logger(f"No pairs found within {threshold} km threshold.")
            return

        # Sort pairs by distance
        pairs_to_merge.sort(key=lambda x: x[2])

        # Merge pairs
        indices_to_drop = set()
        net_validator_count = len(self.aggregated_df)

        for idx1, idx2, dist in pairs_to_merge:
            if idx1 in indices_to_drop or idx2 in indices_to_drop:
                continue  # Skip if already merged

            # Merge idx2 into idx1
            self.aggregated_df.at[idx1, "stake_weight"] += self.aggregated_df.at[idx2, "stake_weight"]
            # self.aggregated_df.at[idx1, "uuid"] += "," + self.aggregated_df.at[idx2, "uuid"]

            # Mark idx2 for dropping
            indices_to_drop.add(idx2)
            merged = True
            self.logger(f"Merged validators at index {idx1} and {idx2}, distance {dist:.2f} km.")

            # Number of validators after merging
            net_validator_count -= 1
            self.logger(f"Validator count after merging: {net_validator_count}")
            if net_validator_count <= 64:
                break

        # Drop merged validators
        if merged:
            self.aggregated_df.drop(list(indices_to_drop), inplace=True)
            self.aggregated_df.reset_index(drop=True, inplace=True)
        else:
            self.logger(f"No validators merged at threshold {threshold} km.")

    def _get_distance_matrix(self, df):
        """
        Calculates the distance matrix for a given DataFrame of validators.

        :param df: DataFrame with 'server_latitude' and 'server_longitude'.
        :return: A symmetric DataFrame representing pairwise distances.
        """
        coords = list(zip(df["latitude"], df["longitude"]))
        dist_matrix = pd.DataFrame(index=range(len(coords)), columns=range(len(coords)))

        for i in range(len(coords)):
            for j in range(i, len(coords)):
                distance = hs.haversine(coords[i], coords[j])
                dist_matrix.at[i, j] = distance
                dist_matrix.at[j, i] = distance  # Symmetric matrix

        return dist_matrix

    def save_results(self, output_file):
        """
        Saves the final aggregated DataFrame to a CSV file.

        :param output_file: Path to the output CSV file.
        """
        self.aggregated_df.to_csv(output_file, index=False)
        self.logger(f"Results saved to {output_file}")


class Preprocessing:
    def __init__(self, input_folder="data/", output_folder="data/pre_processed_data/", server_threshold=500):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.files = self._get_all_files()
        self.server_threshold = server_threshold
        self.log = []

        # Ensure the output folder exists
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        # Empty the processing log file
        open(os.path.join(self.output_folder, "processing_log.txt"), "w").close()

        # Setup logging
        logging.basicConfig(
            filename=os.path.join(self.output_folder, "processing_log.txt"),
            level=logging.INFO,
            format="%(asctime)s - %(message)s",
        )
        self.logger = self.log_message

    def _get_all_files(self):
        """
        Returns a list of all CSV files in the input folder.
        """
        files = [f for f in os.listdir(self.input_folder) if f.endswith(".csv")]
        return files

    def log_message(self, message):
        """
        Logs the message to both the log list and the logging file.

        :param message: The message to log.
        """
        self.log.append(message)
        logging.info(message)
        print(message)

    def process_files(self):
        """
        Processes each file: maps validators to servers, merges validators based on thresholds,
        and saves the processed files into the output folder.
        """
        # Load servers data once
        servers_df = pd.read_csv("servers.csv")

        for file in self.files:
            if file == "servers.csv":
                continue  # Skip the servers file

            self.logger(f"Processing file: {file}")
            validators_df = pd.read_csv(os.path.join(self.input_folder, file))
            self.logger(f"Initial number of validators: {len(validators_df)}")

            # Clean data
            validators_df.dropna(subset=["latitude", "longitude"], inplace=True)
            validators_df["latitude"] = validators_df["latitude"].astype(float)
            validators_df["longitude"] = validators_df["longitude"].astype(float)
            validators_df.reset_index(drop=True, inplace=True)

            # Map validators to servers
            merger = ValidatorMerger(
                validators_df, servers_df, server_threshold=self.server_threshold, logger=self.logger
            )
            merger.map_validators_to_servers()
            merger.aggregate_stake_weights()

            # If number of validators exceeds 64, merge incrementally
            if len(merger.aggregated_df) > 64:
                self.logger(f"Validator count exceeds 64 after initial mapping: {len(merger.aggregated_df)}")
                merger.merge_validators_incrementally(target_count=64)
            else:
                self.logger(f"Validator count is within limit after initial mapping: {len(merger.aggregated_df)}")

            # Save results and logs
            output_file = os.path.join(self.output_folder, f"{file}")
            merger.save_results(output_file)

            self.logger(f"Finished processing file: {file}\n")

        self.logger(f"All files processed. Results saved in {self.output_folder}")


# USAGE
if __name__ == "__main__":
    preprocessing = Preprocessing(
        input_folder="data/pre_processed_data/", output_folder="data/geodec/", server_threshold=500
    )
    preprocessing.process_files()
