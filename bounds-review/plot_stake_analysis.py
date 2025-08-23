import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_stake_thresholds():
    df = pd.read_csv("data/bounds_comparision_stake/stake_analysis.csv")
    
    lambda_values = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
    markers = ['o', 's', '^', 'D', 'v', 'p']
    
    for idx, blockchain in enumerate(df['filename']):
        stakes_33pct = []
        stakes_66pct = []
        
        stakes_33pct.append(df.loc[df['filename'] == blockchain, 'stake_33_percent'].iloc[0])
        stakes_66pct.append(df.loc[df['filename'] == blockchain, 'total_stake_weight'].iloc[0] * 0.66)
        
        for lambda_val in [0.9, 0.8, 0.7, 0.6, 0.5]:
            col_33 = f'min_stake_for_33pct_0{int(lambda_val*10)}linear_weight'
            col_66 = f'min_stake_for_66pct_0{int(lambda_val*10)}linear_weight'
            
            stakes_33pct.append(df.loc[df['filename'] == blockchain, col_33].iloc[0])
            stakes_66pct.append(df.loc[df['filename'] == blockchain, col_66].iloc[0])
        
        ax1.plot(lambda_values, stakes_33pct, color=colors[idx], marker=markers[idx], 
                linewidth=2.5, markersize=8, label=blockchain.capitalize())
        ax2.plot(lambda_values, stakes_66pct, color=colors[idx], marker=markers[idx], 
                linewidth=2.5, markersize=8, label=blockchain.capitalize())
    
    ax1.set_title('33% Liveness Threshold', fontsize=16, pad=20)
    ax1.set_xlabel('Lambda (λ)', fontsize=14)
    ax1.set_ylabel('Minimum Stake Required', fontsize=14)
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=12)
    ax1.set_xlim(0.45, 1.05)
    
    ax2.set_title('66% Safety Threshold', fontsize=16, pad=20)
    ax2.set_xlabel('Lambda (λ)', fontsize=14)
    ax2.set_ylabel('Minimum Stake Required', fontsize=14)
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=12)
    ax2.set_xlim(0.45, 1.05)
    
    # plt.suptitle('Minimum Stake Requirements vs Lambda Values', fontsize=18, y=1.02)
    plt.tight_layout()
    plt.savefig('data/bounds_comparision_stake/stake_thresholds_plot.png', dpi=300, bbox_inches='tight')
    plt.savefig('data/bounds_comparision_stake/stake_thresholds_plot.pdf', bbox_inches='tight')
    plt.show()
    
    print("Plots saved to:")
    print("- data/bounds_comparision_stake/stake_thresholds_plot.png")
    print("- data/bounds_comparision_stake/stake_thresholds_plot.pdf")

if __name__ == "__main__":
    plot_stake_thresholds()