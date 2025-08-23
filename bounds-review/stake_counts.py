import pandas as pd
import os
import glob

def calculate_stake_analysis():
    weights_dir = "data/bounds_comparision/weights/"
    output_dir = "data/bounds_comparision_stake/"
    
    os.makedirs(output_dir, exist_ok=True)
    
    results = []
    
    csv_files = glob.glob(os.path.join(weights_dir, "*.csv"))
    
    for file_path in csv_files:
        filename = os.path.basename(file_path)
        filename_without_ext = os.path.splitext(filename)[0]
        
        try:
            df = pd.read_csv(file_path)
            
            required_cols = ['stake_weight', '0.9linear_weight', '0.8linear_weight', '0.7linear_weight', '0.6linear_weight', '0.5linear_weight']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if not missing_cols:
                total_stake_weight = df['stake_weight'].sum()
                stake_33_percent = total_stake_weight * 0.33
                
                result = {
                    'filename': filename_without_ext,
                    'total_stake_weight': total_stake_weight,
                    'stake_33_percent': stake_33_percent
                }
                
                linear_weights = ['0.9linear_weight', '0.8linear_weight', '0.7linear_weight', '0.6linear_weight', '0.5linear_weight']
                percentages = [0.33, 0.66]
                
                for weight_col in linear_weights:
                    df_sorted = df.sort_values(weight_col, ascending=False)
                    cumsum_linear = df_sorted[weight_col].cumsum()
                    cumsum_stake = df_sorted['stake_weight'].cumsum()
                    
                    total_linear_weight = df[weight_col].sum()
                    
                    for pct in percentages:
                        target_linear_weight = total_linear_weight * pct
                        
                        idx = (cumsum_linear >= target_linear_weight).idxmax()
                        min_stake = cumsum_stake.loc[idx]
                        
                        pct_str = f"{int(pct * 100)}pct"
                        col_name = f'min_stake_for_{pct_str}_{weight_col.replace(".", "")}'
                        result[col_name] = min_stake
                
                results.append(result)
                
                print(f"Processed {filename}: Total={total_stake_weight:.6f}, 33%={stake_33_percent:.6f}")
            else:
                print(f"Warning: Missing columns {missing_cols} in {filename}")
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    
    results_df = pd.DataFrame(results)
    output_file = os.path.join(output_dir, "stake_analysis.csv")
    results_df.to_csv(output_file, index=False)
    
    print(f"\nResults saved to {output_file}")
    print(f"Processed {len(results)} files")
    
    return results_df

if __name__ == "__main__":
    df = calculate_stake_analysis()
    print("\nStake Analysis Summary:")
    print(df)