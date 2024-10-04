import pandas as pd

class DataCleaner:
    def __init__(self, df, logger=None):
        """
        Initializes the DataCleaner class with a pandas DataFrame and a logger.
        
        :param df: pandas DataFrame with 'uuid', 'latitude', 'longitude', 'stake_weight'.
        :param logger: Logger function to handle logging instead of print.
        """
        self.df = df
        self.total_stake_weight = self.df['stake_weight'].sum()
        self.logger = logger if logger else print  # Default to print if no logger provided

    def _merge_duplicate_coordinates(self):
        """
        Merges rows in the DataFrame with the same 'latitude' and 'longitude',
        summing their 'stake_weight'. Logs the number of rows merged.
        """
        # Group by 'latitude' and 'longitude', and sum the 'stake_weight' for duplicates
        merged_df = self.df.groupby(['latitude', 'longitude'], as_index=False).agg({
            'stake_weight': 'sum',
            'uuid': 'first'  # Keep the first 'uuid'
        })
        
        # Calculate the number of rows that have been merged
        original_row_count = len(self.df)
        new_row_count = len(merged_df)
        merged_rows_count = original_row_count - new_row_count
        
        # Log the number of rows merged
        self.logger(f"Number of rows merged due to same latitude, longitude: {merged_rows_count}")
        
        self.df = merged_df

    def _get_total_stake_zero_lat_lon(self):
        """
        Filters the DataFrame for rows where both 'latitude' and 'longitude' are 0,
        and returns the total sum of the 'stake_weight' column for those rows.
        """
        filtered_df = self.df[(self.df['latitude'] == 0) & (self.df['longitude'] == 0)]
        total_stake_zero = filtered_df['stake_weight'].sum()
        return total_stake_zero

    def clean_data(self, threshold_percentage=1.0):
        """
        Cleans the data by:
        1. Removing rows where both 'latitude' and 'longitude' are zero, 
           if the total stake weight for these rows is less than the threshold percentage.
        2. Merging rows with duplicate 'latitude' and 'longitude', summing 'stake_weight'.
        
        Logs the number of data points dropped and the percentage of total stake weight dropped.
        """
        # Fill empty values as zero and convert to float
        self.df[['latitude', 'longitude']] = self.df[['latitude', 'longitude']].fillna(0).astype(float)

        # Get the total stake weight for rows with zero latitude and longitude
        total_stake_zero = self._get_total_stake_zero_lat_lon()

        # Calculate the percentage of stake with zero latitude and longitude
        percentage_zero_stake = (total_stake_zero / self.total_stake_weight) * 100

        # Number of rows and stake to be dropped
        zero_lat_lon_rows = self.df[(self.df['latitude'] == 0) & (self.df['longitude'] == 0)]
        total_rows_to_drop = len(zero_lat_lon_rows)

        # Drop rows if the percentage of zero stake is below the threshold
        if percentage_zero_stake < threshold_percentage:
            self.logger(f"Dropping {total_rows_to_drop} rows with {percentage_zero_stake:.2f}% of total stake.")
            self.df = self.df[(self.df['latitude'] != 0) | (self.df['longitude'] != 0)]
        else:
            self.logger("No rows dropped. Dataset is not reliable")

        # Merge rows with duplicate coordinates
        self._merge_duplicate_coordinates()

        self.logger(f"No. of rows post data cleaning: {len(self.df)}")

    def get_cleaned_data(self):
        """
        Returns the cleaned DataFrame after applying the cleaning rules.

        :return: Cleaned pandas DataFrame
        """
        return self.df