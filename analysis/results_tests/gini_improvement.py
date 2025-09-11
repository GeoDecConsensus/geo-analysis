import numpy as np
import pandas as pd


def compute_gini_improvement(gini_file_path, output_folder="results"):
    """
    Compute Gini improvement percentages per blockchain and overall averages.

    :param gini_file_path: Path to the CSV file containing Gini coefficients.
    :param output_folder: Folder to save the results.
    """
    # Load the Gini coefficient file
    gini_df = pd.read_csv(gini_file_path)

    # Define old and new Gini columns
    old_columns = ["stake_weight"]  # Old Gini column (Run 1)
    new_columns = [
        "stake_weight",
        "0.8linear_weight",
        "0.6linear_weight",
        "0.4linear_weight",
        "0.2linear_weight",
        "0linear_weight",
    ]

    # Extract old Gini values (Run 1)
    old_gini_df = gini_df[["file"] + old_columns].copy()

    # Extract new Gini values (Runs 1, 3, 5, 7, 8, 9)
    new_gini_df = gini_df[["file"] + new_columns].copy()

    # Initialize a list to store average improvement percentages per blockchain
    gini_improvement_averages = []

    # Calculate improvement percentage for each blockchain
    for idx, blockchain in enumerate(old_gini_df["file"]):
        # Extract old and new Gini values for the blockchain
        old_gini_value = old_gini_df.loc[idx, "stake_weight"]
        new_gini_values = new_gini_df.loc[idx, new_columns].values[1:]  # Exclude the first value (Run 1)

        # Compute improvement percentages: (new Gini - old Gini) / old Gini
        improvement_percentages = (old_gini_value - new_gini_values) / old_gini_value

        # Take the average improvement percentage across all lambda values
        average_improvement = np.mean(improvement_percentages)

        # Append the average improvement percentage for the blockchain
        gini_improvement_averages.append(average_improvement)

    # Calculate the range of the averages
    gini_improvement_range = np.max(gini_improvement_averages) - np.min(gini_improvement_averages)

    # Calculate the overall average improvement percentage across all blockchains
    overall_average_improvement = np.mean(gini_improvement_averages)

    # Prepare the result DataFrame
    result_df = pd.DataFrame({"file": old_gini_df["file"], "average_improvement": gini_improvement_averages})

    # Save the results
    result_file_path = f"{output_folder}/gini_improvement_results.csv"
    result_df.to_csv(result_file_path, index=False)
    print(f"Results saved to {result_file_path}")

    # Print the results
    print("Gini Improvement Percentages per Blockchain:")
    print(result_df)
    print("\nRange of Gini Improvement Percentages:", gini_improvement_range)
    print("Overall Average Gini Improvement Percentage:", overall_average_improvement)

    return result_df, gini_improvement_range, overall_average_improvement


# Usage Example
if __name__ == "__main__":
    # Path to the Gini coefficient file
    gini_file_path = "results/centrality_measures_wc.csv"  # Replace with your file path
    output_folder = "results"  # Folder to save the outputs

    # Create the output folder if it doesn't exist
    import os

    os.makedirs(output_folder, exist_ok=True)

    # Compute Gini improvements
    compute_gini_improvement(gini_file_path, output_folder)
