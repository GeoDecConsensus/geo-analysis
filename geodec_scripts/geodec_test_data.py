import logging
import os
from datetime import datetime

import pandas as pd

from pre_processing.gdi_calculator import GDI_Calculator
from utils.normalization import Normalization
from utils.weight_computation import WeightComputation


class Preprocessing:
    def __init__(self, input_folder="data/geodec_merged/", output_folder="data/geodec_tests_2/"):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.files = self._get_all_files()
        self.logger = self._setup_logger()

        # Ensure the output folder exists
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def _get_all_files(self):
        """
        Returns a list of all CSV files in the input folder.
        """
        files = [f for f in os.listdir(self.input_folder) if f.endswith(".csv")]
        return files

    def _setup_logger(self):
        """
        Sets up the logging configuration and returns a logger instance.
        """
        log_file = os.path.join(self.output_folder, "processing_log.txt")
        open(log_file, "w").close()  # Empty the processing log file

        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format="%(asctime)s - %(message)s",
        )
        return logging.getLogger()

    def process_file(self, file):
        """
        Processes an individual CSV file for GDI calculation and normalization.
        """
        try:
            # Read the CSV file
            self.logger.info(f"Reading CSV file {file}...")
            df = pd.read_csv(os.path.join(self.input_folder, file))

            # Calculate GDI
            self.logger.info(f"Calculating GDI for {file}...")
            gdi_calc = GDI_Calculator(df, self.logger)
            df_with_gdi = gdi_calc.calculate_GDI()

            # Calculate weights
            self.logger.info(f"Computing weights for {file}...")
            weight_comp = WeightComputation(df_with_gdi)
            df_with_weights = weight_comp.get_updated_df()

            final_df = df_with_weights.copy()

            # Log statistics and normalize weight columns
            for col in df_with_weights.columns:
                if "weight" in col.lower():
                    final_df = Normalization.normalize_columnToInteger(df_with_weights, col)
                    self.logger.info(f"{col} for {file}: Mean={final_df[col].mean():.2f}")

            # Save the processed data to CSV
            output_filename = os.path.join(self.output_folder, f"{file}")
            final_df.to_csv(output_filename, index=False)
            self.logger.info(f"Results saved to {output_filename}")

        except Exception as e:
            self.logger.error(f"An error occurred while processing {file}: {str(e)}", exc_info=True)

    def process_all_files(self):
        """
        Processes all CSV files in the input folder.
        """
        for file in self.files:
            self.process_file(file)


# USAGE
if __name__ == "__main__":
    preprocessing = Preprocessing()  # Default input and output folders
    preprocessing.process_all_files()
