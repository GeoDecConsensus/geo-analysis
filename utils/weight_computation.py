import os

import pandas as pd

from utils.normalization import Normalization


class WeightComputation:
    def __init__(self, df):
        """
        Initialize the WeightComputation class with a pandas DataFrame.

        :param df: A pandas DataFrame with 'stake_weight' and 'GDI' columns.
        """
        self.df = df

    def compute_linear_weight(self, lambdas=[1, 0.8, 0.6, 0.4, 0.2, 0]):
        """
        Compute lambda * stake_weight + (1 - lambda) * GDI and add as new columns.

        :param lambdas: List of lambda values for linear weighting.
        """
        # Filter the required lambda values (Run 1, 3, 5, 7, 8, 9)
        selected_lambdas = [1, 0.8, 0.6, 0.4, 0.2, 0]

        for i in selected_lambdas:
            column_name = f"{i}linear_weight"
            self.df[column_name] = i * self.df["stake_weight"] + (1 - i) * self.df["GDI"]

    def get_updated_df(self):
        """
        Return the DataFrame after computing the weights.

        :return: Updated DataFrame.
        """
        # Normalize 'stake_weight' and 'GDI' columns
        self.df = Normalization.normalize_column(self.df, col="stake_weight")
        self.df = Normalization.normalize_column(self.df, col="GDI")
        print(f"Normalized Data:\n{self.df.head()}")

        # Calculate weights for selected lambdas
        self.compute_linear_weight()

        return self.df


def get_all_files(folder_path):
    """
    Returns a list of all CSV files in the specified folder.

    :param folder_path: Path to the folder containing CSV files.
    :return: List of CSV files.
    """
    return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f.endswith(".csv")]


# Input and output folder paths
input_folder = "data/pre_processed_data/"
output_folder = "data/wc/"

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Get all CSV files in the input folder
files = get_all_files(input_folder)

for file in files:
    # Read the CSV file
    df = pd.read_csv(os.path.join(input_folder, file))
    print(f"Processing File: {file}")

    # Initialize the WeightComputation class
    wc = WeightComputation(df)

    # Get the updated DataFrame with computed weights
    updated_df = wc.get_updated_df()

    # Save the updated DataFrame to the output folder
    output_file_path = os.path.join(output_folder, file)
    updated_df.to_csv(output_file_path, index=False)
    print(f"Saved updated file to: {output_file_path}")
