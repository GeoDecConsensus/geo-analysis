import pandas as pd

class Normalization:
    
    @staticmethod
    def normalize_columns(df):
        """
        Normalizes both the 'GDI' and 'stake_weight' columns by dividing each value 
        by the total sum of their respective columns, updating the original DataFrame.
        
        :param df: A pandas DataFrame with 'GDI' and 'stake_weight' columns.
        :return: The updated DataFrame with normalized 'GDI' and 'stake_weight' columns.
        :raises ValueError: If either 'GDI' or 'stake_weight' columns do not exist.
        """
        # Check if both columns exist in the DataFrame
        required_columns = ['GDI', 'stake_weight']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"'{col}' column is missing. Both 'GDI' and 'stake_weight' columns are required.")
        
        # Normalize 'GDI'
        total_gdi = df['GDI'].sum()
        df['GDI'] = df['GDI'] / total_gdi

        # Normalize 'stake_weight'
        total_stake_weight = df['stake_weight'].sum()
        df['stake_weight'] = df['stake_weight'] / total_stake_weight

        return df
