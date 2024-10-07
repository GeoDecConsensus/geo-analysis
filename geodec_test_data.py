import logging
import os
from datetime import datetime

import pandas as pd

from pre_processing.gdi_calculator import GDI_Calculator
from utils.normalization import Normalization
from utils.weight_computation import WeightComputation

OUTPUT_FOLDER = "data/geodec_tests/"

# Ensure the output folder exists
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# Empty the processing log file
open(os.path.join(OUTPUT_FOLDER, "processing_log.txt"), "w").close()

# Set up logging
logging.basicConfig(
    filename=os.path.join(OUTPUT_FOLDER, "processing_log.txt"),
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)
logger = logging.getLogger()


def _get_all_files(self):
    """
    Returns a list of all CSV files in the input folder.
    """
    files = [f for f in os.listdir(self.input_folder) if f.endswith(".csv")]
    return files


def main():
    try:
        # Read the CSV file
        logger.info("Reading CSV file...")
        df = pd.read_csv("data/geodec/solana.csv")

        # Calculate GDI
        logger.info("Calculating GDI...")
        gdi_calc = GDI_Calculator(df, logger)
        df_with_gdi = gdi_calc.calculate_GDI()

        # Calculate weights
        logger.info("Computing weights...")
        weight_comp = WeightComputation(df_with_gdi)
        df_with_weights = weight_comp.get_updated_df()

        final_df = df_with_weights.copy()

        # Log some statistics
        logger.info(f"Statistics of calculated weights:")
        for col in df_with_weights.columns:
            if "weight" in col.lower():
                final_df = Normalization.normalize_columnToInteger(df_with_weights, col)
                logger.info(f"{col}: Mean={final_df[col].mean():.2f}")

        # Save to CSV
        output_filename = f"{OUTPUT_FOLDER}solana.csv"
        final_df.to_csv(output_filename, index=False)
        logger.info(f"Results saved to {output_filename}")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()
