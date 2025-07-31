# GDI Sensitivity Analysis: 20km Threshold Justification

## Methodology

This analysis evaluates the sensitivity of the Geospatial Diversity Index (GDI) to validator merging distance thresholds. The study addresses reviewer concerns about the justification for the 20km merging radius.

**Process:**
1. **Data Processing**: For each blockchain dataset, validators are cleaned using a 33% stake threshold
2. **Distance Merging**: Validators within specified distance thresholds are merged using Haversine distance
3. **GDI Calculation**: GDI computed for each validator based on distances to nodes forming 2/3 of total stake
4. **Correlation Analysis**: Pearson correlations calculated between 20km baseline and alternative thresholds
5. **Thresholds Tested**: [10, 15, 20, 25, 30] km

## Files

**Input Files:**
- `data/aptos.csv`
- `data/avalanche.csv`
- `data/ethereum.csv`
- `data/ethernodes.csv`
- `data/solana.csv`
- `data/sui.csv`

**Output Files:**
- `results/sensitivity_analysis_results/sensitivity_analysis_report.md` - This report
- `results/sensitivity_analysis_results/overall_summary_statistics.csv` - Summary statistics across all datasets
- `results/sensitivity_analysis_results/aptos_*` - Individual dataset results (CSV, PNG plots)
- `results/sensitivity_analysis_results/avalanche_*` - Individual dataset results (CSV, PNG plots)
- `results/sensitivity_analysis_results/ethereum_*` - Individual dataset results (CSV, PNG plots)
- `results/sensitivity_analysis_results/ethernodes_*` - Individual dataset results (CSV, PNG plots)
- `results/sensitivity_analysis_results/solana_*` - Individual dataset results (CSV, PNG plots)
- `results/sensitivity_analysis_results/sui_*` - Individual dataset results (CSV, PNG plots)

## Executive Summary

**Conclusion**: **REASONABLY JUSTIFIED**: Moderate correlation with alternative thresholds
**Overall Average Correlation**: 0.877
**Impact Level**: Moderate impact on decentralization metrics
**Datasets Analyzed**: 6 blockchain networks

## Detailed Results by Blockchain

### APTOS
- **Average Correlation with 20km**: 0.965
- **Average P-value**: 0.0000
- **Correlations**: 10km: 0.961, 15km: 0.961, 25km: 0.970, 30km: 0.967
- **P-values**: 10km: 0.0000, 15km: 0.0000, 25km: 0.0000, 30km: 0.0000

### AVALANCHE
- **Average Correlation with 20km**: 0.831
- **Average P-value**: 0.0000
- **Correlations**: 10km: 0.814, 15km: 0.833, 25km: 0.840, 30km: 0.839
- **P-values**: 10km: 0.0000, 15km: 0.0000, 25km: 0.0000, 30km: 0.0000

### ETHEREUM
- **Average Correlation with 20km**: 0.809
- **Average P-value**: 0.0000
- **Correlations**: 10km: 0.762, 15km: 0.863, 25km: 0.803, 30km: 0.807
- **P-values**: 10km: 0.0000, 15km: 0.0000, 25km: 0.0000, 30km: 0.0000

### ETHERNODES
- **Average Correlation with 20km**: 0.875
- **Average P-value**: 0.0000
- **Correlations**: 10km: 0.858, 15km: 0.869, 25km: 0.897, 30km: 0.875
- **P-values**: 10km: 0.0000, 15km: 0.0000, 25km: 0.0000, 30km: 0.0000

### SOLANA
- **Average Correlation with 20km**: 0.871
- **Average P-value**: 0.0000
- **Correlations**: 10km: 0.796, 15km: 0.907, 25km: 0.953, 30km: 0.829
- **P-values**: 10km: 0.0000, 15km: 0.0000, 25km: 0.0000, 30km: 0.0000

### SUI
- **Average Correlation with 20km**: 0.911
- **Average P-value**: 0.0000
- **Correlations**: 10km: 0.881, 15km: 0.881, 25km: 1.000, 30km: 0.882
- **P-values**: 10km: 0.0000, 15km: 0.0000, 25km: 0.0000, 30km: 0.0000

## Summary Statistics

### Average Correlations by Chain
- **aptos**: 0.965 ***
- **sui**: 0.911 ***
- **ethernodes**: 0.875 ***
- **solana**: 0.871 ***
- **avalanche**: 0.831 ***
- **ethereum**: 0.809 ***

*Significance levels: *** p<0.001, ** p<0.01, * p<0.05*

### Overall Statistics
- **Mean correlation**: 0.877
- **Median correlation**: 0.873
- **Standard deviation**: 0.051
- **Range**: 0.809 - 0.965
- **Significant correlations (p<0.05)**: 6/6

## Interpretation

The 20km threshold is **reasonably justified** with moderate sensitivity to threshold choice. While alternative thresholds show good correlation, some variation in GDI rankings occurs.

**Highly stable chains** (r > 0.9): sui, aptos
