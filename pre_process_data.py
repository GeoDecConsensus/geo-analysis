import os
import pandas as pd

from data_cleaner import DataCleaner
from gdi_calculator import GDI_Calculator
from normalization import Normalization
class Preprocessing:
    def __init__(self, input_folder='data/', output_folder='pre_processed_data/'):
        self.input_folder = input_folder
        self.files = self._get_all_files()
        self.output_folder = output_folder
        self.log = []

        # Ensure the output folder exists
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
    
    def _get_all_files(self):
        """
        This function returns a list of all files in the given folder path.
        
        :param folder_path: Path to the folder
        :return: List of files in the folder
        """
        # Get a list of all files in the folder
        files = [f for f in os.listdir(self.input_folder) if os.path.isfile(os.path.join(self.input_folder, f))]
        return files

    
    def log_message(self, message):
        """
        Log the message for future saving.
        :param message: The message to log.
        """
        self.log.append(message)
        print(message)

    def process_files(self):
        """
        Process each file for data cleaning, GDI calculation, and normalization,
        then save the processed files into the pre_processed_data folder.
        """
        for file in self.files:
            df = pd.read_csv(os.path.join(self.input_folder, file))
            self.log_message(f'{file} rows: {len(df)}')

            # Clean the data with the logger passed down
            cleaner = DataCleaner(df, logger=self.log_message)
            # 1. If latitude, longitude are missing, drop them. Format them in float.    
            # 2. If latitude and longitude are same value, merge them and add stake weight
            cleaner.clean_data(threshold_percentage=33.0)
            cleaned_df = cleaner.get_cleaned_data()

            # Distance and GDI Calculations for validators
            gdi_calculator = GDI_Calculator(cleaned_df, logger=self.log_message)
            # Merge validators within 20km proximity (units=km)
            # NOTE: 20km is arbitrary, can be any value  
            gdi_calculator.merge_closest_validators(threshold_distance=20)
            gdi_results = gdi_calculator.calculate_GDI()

            # Normalize 'GDI' and 'stake_weight' columns
            normalized_df = Normalization.normalize_columns(gdi_results)

            # Save normalized data to CSV
            output_file_path = os.path.join(self.output_folder, file)
            normalized_df.to_csv(output_file_path, index=False)
            self.log_message(f'File saved: {output_file_path}\n')

        # Print where the files are saved
        self.log_message(f"Files stored in: {self.output_folder}")

        # Save all logs to a log file
        self.save_logs()

    def save_logs(self):
        """
        Save the log messages to a log file in the pre_processed_data folder.
        """
        log_file = os.path.join(self.output_folder, 'preprocessing_log.txt')
        with open(log_file, 'w') as f:
            for entry in self.log:
                f.write(entry + '\n')
        print(f"Log saved to: {log_file}")


# Example usage
preprocessing = Preprocessing()
preprocessing.process_files()