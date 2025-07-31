import os
import pandas as pd
import numpy as np
from scipy.stats import pearsonr, spearmanr
import scipy.stats as stats
from data_cleaner import DataCleaner
from gdi_calculator import GDI_Calculator
import matplotlib.pyplot as plt
import seaborn as sns

class GDI_SensitivityAnalysis:
    def __init__(self, input_folder='data/', output_folder='results/sensitivity_analysis_results/'):
        self.input_folder = input_folder
        self.files = self._get_all_files()
        self.output_folder = output_folder
        self.distance_thresholds = [10, 15, 20, 25, 30]  # km
        self.results = {}
        
        # Ensure the output folder exists
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
    
    def _get_all_files(self):
        """Get all CSV files in the input folder with expected columns."""
        files = []
        for f in os.listdir(self.input_folder):
            if os.path.isfile(os.path.join(self.input_folder, f)) and f.endswith('.csv'):
                try:
                    # Check if file has expected columns
                    df = pd.read_csv(os.path.join(self.input_folder, f), encoding='ISO-8859-1', nrows=1)
                    if all(col in df.columns for col in ['uuid', 'stake_weight', 'latitude', 'longitude']):
                        files.append(f)
                except:
                    continue
        return files
    
    def calculate_gdi_for_distance(self, df, distance_threshold):
        """Calculate GDI for a specific distance threshold."""
        # Clean the data
        cleaner = DataCleaner(df.copy())
        cleaner.clean_data(threshold_percentage=33.0)
        cleaned_df = cleaner.get_cleaned_data()
        
        # Calculate GDI with the specified distance threshold
        gdi_calculator = GDI_Calculator(cleaned_df)
        gdi_calculator.merge_closest_validators(threshold_distance=distance_threshold)
        gdi_results = gdi_calculator.calculate_GDI()
        
        return gdi_results
    
    def run_sensitivity_analysis(self):
        """Run sensitivity analysis for all files and distance thresholds."""
        print("Starting GDI Sensitivity Analysis...")
        print(f"Testing distance thresholds: {self.distance_thresholds} km")
        
        for file in self.files:
            print(f"\nProcessing file: {file}")
            df = pd.read_csv(os.path.join(self.input_folder, file), encoding='ISO-8859-1')
            
            file_results = {}
            gdi_values = {}
            
            # Calculate GDI for each distance threshold
            for distance in self.distance_thresholds:
                print(f"  Testing {distance}km threshold...")
                gdi_results = self.calculate_gdi_for_distance(df, distance)
                
                # Store the GDI values
                gdi_values[f'{distance}km'] = gdi_results['GDI'].values
                
                # Store summary statistics
                file_results[distance] = {
                    'mean_gdi': gdi_results['GDI'].mean(),
                    'std_gdi': gdi_results['GDI'].std(),
                    'min_gdi': gdi_results['GDI'].min(),
                    'max_gdi': gdi_results['GDI'].max(),
                    'num_validators': len(gdi_results)
                }
            
            # Calculate correlation matrix (pad shorter arrays with NaN)
            max_len = max(len(arr) for arr in gdi_values.values())
            padded_values = {}
            for key, arr in gdi_values.items():
                padded = np.full(max_len, np.nan)
                padded[:len(arr)] = arr
                padded_values[key] = padded
            
            gdi_df = pd.DataFrame(padded_values)
            correlation_matrix = gdi_df.corr()
            
            # Store results for this file
            self.results[file] = {
                'summary_stats': file_results,
                'gdi_values': padded_values,
                'correlation_matrix': correlation_matrix
            }
            
            # Save individual file results
            self._save_file_results(file, file_results, correlation_matrix, gdi_df)
        
        # Generate overall analysis report
        self._generate_overall_report()
        print(f"\nSensitivity analysis complete! Results saved in: {self.output_folder}")
    
    
    def _save_file_results(self, filename, summary_stats, correlation_matrix, gdi_df):
        """Save results for a specific file."""
        base_name = filename.replace('.csv', '')
        
        # Save summary statistics
        summary_df = pd.DataFrame(summary_stats).T
        summary_df.to_csv(os.path.join(self.output_folder, f'{base_name}_summary_stats.csv'))
        
        # Save correlation matrix
        correlation_matrix.to_csv(os.path.join(self.output_folder, f'{base_name}_correlation_matrix.csv'))
        
        # Save GDI values for all thresholds
        gdi_df.to_csv(os.path.join(self.output_folder, f'{base_name}_gdi_values.csv'), index=False)
        
        # Create correlation heatmap
        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                   square=True, fmt='.3f')
        plt.title(f'GDI Correlation Matrix - {base_name}')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_folder, f'{base_name}_correlation_heatmap.png'), dpi=300)
        plt.close()
        
        # Create GDI distribution plot
        plt.figure(figsize=(12, 8))
        for col in gdi_df.columns:
            plt.hist(gdi_df[col], alpha=0.7, label=col, density=True)
        plt.xlabel('GDI Value')
        
        plt.ylabel('Density')
        plt.title(f'GDI Distribution by Distance Threshold - {base_name}')
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_folder, f'{base_name}_gdi_distributions.png'), dpi=300)
        plt.close()
    
    def _generate_overall_report(self):
        """Generate a detailed sensitivity analysis report addressing the 20km threshold justification."""
        report_lines = []
        report_lines.append("# GDI Sensitivity Analysis: 20km Threshold Justification\n\n")
        
        # Methodology section
        report_lines.append("## Methodology\n\n")
        report_lines.append("This analysis evaluates the sensitivity of the Geospatial Diversity Index (GDI) to validator merging distance thresholds. ")
        report_lines.append("The study addresses reviewer concerns about the justification for the 20km merging radius.\n\n")
        report_lines.append("**Process:**\n")
        report_lines.append("1. **Data Processing**: For each blockchain dataset, validators are cleaned using a 33% stake threshold\n")
        report_lines.append("2. **Distance Merging**: Validators within specified distance thresholds are merged using Haversine distance\n")
        report_lines.append("3. **GDI Calculation**: GDI computed for each validator based on distances to nodes forming 2/3 of total stake\n")
        report_lines.append("4. **Correlation Analysis**: Pearson correlations calculated between 20km baseline and alternative thresholds\n")
        report_lines.append(f"5. **Thresholds Tested**: {self.distance_thresholds} km\n\n")
        
        # Input/Output Files
        report_lines.append("## Files\n\n")
        report_lines.append("**Input Files:**\n")
        for file in sorted(self.files):
            report_lines.append(f"- `{self.input_folder}{file}`\n")
        report_lines.append("\n**Output Files:**\n")
        report_lines.append(f"- `{self.output_folder}sensitivity_analysis_report.md` - This report\n")
        report_lines.append(f"- `{self.output_folder}overall_summary_statistics.csv` - Summary statistics across all datasets\n")
        for file in sorted(self.files):
            base_name = file.replace('.csv', '')
            report_lines.append(f"- `{self.output_folder}{base_name}_*` - Individual dataset results (CSV, PNG plots)\n")
        report_lines.append("\n")
        
        # Calculate detailed correlations with 20km baseline
        all_20km_corrs = []
        chain_results = {}
        
        for file, results in self.results.items():
            if '20km' in results['gdi_values']:
                chain_name = file.replace('.csv', '')
                chain_corrs = []
                chain_pvals = []
                
                for threshold in self.distance_thresholds:
                    if threshold != 20:
                        # Remove NaN values for correlation calculation
                        x = np.array(results['gdi_values']['20km'])
                        y = np.array(results['gdi_values'][f'{threshold}km'])
                        mask = ~(np.isnan(x) | np.isnan(y))
                        if np.sum(mask) > 1:  # Need at least 2 valid points
                            corr, p_val = pearsonr(x[mask], y[mask])
                            all_20km_corrs.append(corr)
                            chain_corrs.append(corr)
                            chain_pvals.append(p_val)
                
                chain_results[chain_name] = {
                    'correlations': chain_corrs,
                    'p_values': chain_pvals,
                    'avg_correlation': np.mean(chain_corrs) if chain_corrs else 0,
                    'avg_p_value': np.mean(chain_pvals) if chain_pvals else 1
                }
        
        overall_avg_corr = np.mean(all_20km_corrs) if all_20km_corrs else 0
        
        # Executive Summary
        report_lines.append("## Executive Summary\n\n")
        if overall_avg_corr > 0.95:
            justification = "**WELL-JUSTIFIED**: Alternative thresholds produce nearly identical GDI values"
            impact = "minimal"
        elif overall_avg_corr > 0.85:
            justification = "**REASONABLY JUSTIFIED**: Moderate correlation with alternative thresholds"
            impact = "moderate"
        else:
            justification = "**REQUIRES STRONG RATIONALE**: Low correlation with alternative thresholds"
            impact = "significant"
        
        report_lines.append(f"**Conclusion**: {justification}\n")
        report_lines.append(f"**Overall Average Correlation**: {overall_avg_corr:.3f}\n")
        report_lines.append(f"**Impact Level**: {impact.capitalize()} impact on decentralization metrics\n")
        report_lines.append(f"**Datasets Analyzed**: {len(self.files)} blockchain networks\n\n")
        
        # Detailed Results by Chain
        report_lines.append("## Detailed Results by Blockchain\n\n")
        
        for chain_name, chain_data in sorted(chain_results.items()):
            report_lines.append(f"### {chain_name.upper()}\n")
            report_lines.append(f"- **Average Correlation with 20km**: {chain_data['avg_correlation']:.3f}\n")
            report_lines.append(f"- **Average P-value**: {chain_data['avg_p_value']:.4f}\n")
            
            # Individual threshold correlations with p-values
            corr_details = []
            p_val_details = []
            threshold_idx = 0
            for threshold in self.distance_thresholds:
                if threshold != 20 and threshold_idx < len(chain_data['correlations']):
                    corr = chain_data['correlations'][threshold_idx]
                    p_val = chain_data['p_values'][threshold_idx]
                    corr_details.append(f"{threshold}km: {corr:.3f}")
                    p_val_details.append(f"{threshold}km: {p_val:.4f}")
                    threshold_idx += 1
            
            report_lines.append(f"- **Correlations**: {', '.join(corr_details)}\n")
            report_lines.append(f"- **P-values**: {', '.join(p_val_details)}\n\n")
        
        # Summary Statistics
        report_lines.append("## Summary Statistics\n\n")
        
        # Chain averages
        report_lines.append("### Average Correlations by Chain\n")
        for chain_name, chain_data in sorted(chain_results.items(), key=lambda x: x[1]['avg_correlation'], reverse=True):
            significance = "***" if chain_data['avg_p_value'] < 0.001 else "**" if chain_data['avg_p_value'] < 0.01 else "*" if chain_data['avg_p_value'] < 0.05 else ""
            report_lines.append(f"- **{chain_name}**: {chain_data['avg_correlation']:.3f} {significance}\n")
        
        report_lines.append("\n*Significance levels: *** p<0.001, ** p<0.01, * p<0.05*\n\n")
        
        # Statistical summary
        all_chain_avgs = [data['avg_correlation'] for data in chain_results.values()]
        all_p_values = [data['avg_p_value'] for data in chain_results.values()]
        
        report_lines.append("### Overall Statistics\n")
        report_lines.append(f"- **Mean correlation**: {np.mean(all_chain_avgs):.3f}\n")
        report_lines.append(f"- **Median correlation**: {np.median(all_chain_avgs):.3f}\n")
        report_lines.append(f"- **Standard deviation**: {np.std(all_chain_avgs):.3f}\n")
        report_lines.append(f"- **Range**: {np.min(all_chain_avgs):.3f} - {np.max(all_chain_avgs):.3f}\n")
        report_lines.append(f"- **Significant correlations (p<0.05)**: {sum(1 for p in all_p_values if p < 0.05)}/{len(all_p_values)}\n\n")
        
        # Interpretation
        report_lines.append("## Interpretation\n\n")
        if overall_avg_corr > 0.95:
            report_lines.append("The 20km threshold is **well-justified** as alternative thresholds produce nearly identical GDI rankings. ")
            report_lines.append("The choice of merging radius has minimal impact on decentralization assessment.\n\n")
        elif overall_avg_corr > 0.85:
            report_lines.append("The 20km threshold is **reasonably justified** with moderate sensitivity to threshold choice. ")
            report_lines.append("While alternative thresholds show good correlation, some variation in GDI rankings occurs.\n\n")
        else:
            report_lines.append("The 20km threshold shows **high sensitivity**. Strong justification is needed as different ")
            report_lines.append("thresholds significantly impact decentralization metrics and validator rankings.\n\n")
        
        high_corr_chains = [name for name, data in chain_results.items() if data['avg_correlation'] > 0.9]
        if high_corr_chains:
            report_lines.append(f"**Highly stable chains** (r > 0.9): {', '.join(high_corr_chains)}\n")
        
        low_corr_chains = [name for name, data in chain_results.items() if data['avg_correlation'] < 0.8]
        if low_corr_chains:
            report_lines.append(f"**Sensitive chains** (r < 0.8): {', '.join(low_corr_chains)}\n")
        
        # Save the report
        with open(os.path.join(self.output_folder, 'sensitivity_analysis_report.md'), 'w') as f:
            f.writelines(report_lines)
        
        # Create overall summary statistics table
        overall_summary = []
        for file, results in self.results.items():
            for distance, stats in results['summary_stats'].items():
                row = {'file': file, 'distance_km': distance, **stats}
                overall_summary.append(row)
        
        overall_df = pd.DataFrame(overall_summary)
        overall_df.to_csv(os.path.join(self.output_folder, 'overall_summary_statistics.csv'), index=False)

if __name__ == "__main__":
    analyzer = GDI_SensitivityAnalysis()
    analyzer.run_sensitivity_analysis()