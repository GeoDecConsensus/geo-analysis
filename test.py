import pandas as pd
import os

from data_cleaner import DataCleaner
from gdi_calculator import GDI_Calculator
from normalization import Normalization

def get_all_files(folder_path):
    """
    This function returns a list of all files in the given folder path.
    
    :param folder_path: Path to the folder
    :return: List of files in the folder
    """
    # Get a list of all files in the folder
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    return files

# files = get_all_files('data/')
files = ['sui.csv', 'aptos.csv']

for file in files:    
    df = pd.read_csv('data/'+file)
    print(file, 'rows:', len(df))
    
    # Clean the data
    # 1. If latitude, longitude are missing, drop them.   
    # 2. If latitude and longitude are same value, merge them and add stake weight
    cleaner = DataCleaner(df)
    cleaner.clean_data(threshold_percentage=33.0)
    cleaned_df = cleaner.get_cleaned_data()
    
    # Get the GDI class for distances computation     
    gdi_calculator = GDI_Calculator(cleaned_df)
    
    # Merge validators within 20km proximity (units=km)
    # NOTE: 20km is arbitrary, can be any value  
    gdi_calculator.merge_closest_validators(threshold_distance=20)
    # Calculate the GDI
    gdi_results = gdi_calculator.calculate_GDI()
    
    # normalizes 'GDI' and 'stake_weight' columns
    normalized_df = Normalization.normalize_columns(gdi_results)

    # View the updated dataframe
    # print(normalized_df)