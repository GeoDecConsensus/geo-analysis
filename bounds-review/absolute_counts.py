import os
import pandas as pd
import math

# Directory containing the weights CSVs
DATA_DIR = 'data/bounds_comparision/weights'
# Output directory and file
OUTPUT_DIR = 'data/bounds_comparision'
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'bounds_comparison.csv')

# Columns to check for 33% coverage
WEIGHT_COLS = [
    'stake_weight',
    '0.9linear_weight',
    '0.8linear_weight',
    '0.7linear_weight',
    '0.6linear_weight',
    '0.5linear_weight',
]

def percent_validators_for_threshold(df, col, threshold=0.33):
    values = df[col].astype(float).sort_values(ascending=False)
    total = values.sum()
    if total == 0:
        return 0.0
    cumsum = values.cumsum()
    num_needed = (cumsum < threshold * total).sum() + 1  # +1 to include the first that passes threshold
    return 100.0 * num_needed / len(values) if len(values) > 0 else 0.0

def analyze_file(filepath):
    df = pd.read_csv(filepath)
    num_validators = len(df)
    num_validators_33pct = math.ceil(num_validators * 0.33)
    result = {
        'file': os.path.basename(filepath),
        'num_validators': num_validators,
        'num_validators_33pct': num_validators_33pct,
    }
    for col in WEIGHT_COLS:
        if col in df.columns:
            pct = percent_validators_for_threshold(df, col)
            result[f'pct_validators_33pct_{col}'] = pct
        else:
            result[f'pct_validators_33pct_{col}'] = None
    return result

def main():
    results = []
    for fname in os.listdir(DATA_DIR):
        if fname.endswith('.csv'):
            fpath = os.path.join(DATA_DIR, fname)
            results.append(analyze_file(fpath))
    df_results = pd.DataFrame(results)
    # Print as a table
    print(df_results.to_string(index=False))
    # Save to CSV
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df_results.to_csv(OUTPUT_FILE, index=False)
    print(f"\nResults saved to {OUTPUT_FILE}")

if __name__ == '__main__':
    main() 