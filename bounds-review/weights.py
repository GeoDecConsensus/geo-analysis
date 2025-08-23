import os
import pandas as pd
from utils.weight_computation import WeightComputation

# Input and output directories
input_dir = 'data/pre_processed_data'
output_dir = 'data/bounds_comparision/weights'

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# List all CSV files in the input directory
csv_files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]

for csv_file in csv_files:
    input_path = os.path.join(input_dir, csv_file)
    output_path = os.path.join(output_dir, csv_file)
    print(f'Processing {csv_file}...')
    df = pd.read_csv(input_path)
    wc = WeightComputation(df)
    updated_df = wc.get_updated_df()
    updated_df.to_csv(output_path, index=False)
    print(f'Saved to {output_path}')
