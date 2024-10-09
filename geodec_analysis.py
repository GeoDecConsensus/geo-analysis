import matplotlib.pyplot as plt
import pandas as pd

# Load the data from a CSV file
# Ensure your CSV file is in the same directory or provide the correct path
df = pd.read_csv('data/geodec_run/aptos.csv')

# Remove rows where 'runs' column has missing values
df_clean = df.dropna(subset=['runs'])

# Define titles for each run
titles = ['stake_weight', '0.9linear_weight', '0.8linear_weight', '0.7linear_weight', '0.6linear_weight', '0.5linear_weight',
          '0.9exponential_weight', '0.8exponential_weight', '0.7exponential_weight', '0.6exponential_weight', '0.5exponential_weight']
df_clean['title'] = titles

# Plot graphs
plt.figure(figsize=(15, 10))

# Plot for consensus_tps
plt.subplot(2, 2, 1)
plt.plot(df_clean['title'], df_clean['consensus_tps'], marker='o')
plt.title('Consensus TPS')
plt.xticks(rotation=45, ha="right")
plt.xlabel('Tests')
plt.ylabel('TPS')

# Plot for consensus_latency
plt.subplot(2, 2, 2)
plt.plot(df_clean['title'], df_clean['consensus_latency'], marker='o', color='orange')
plt.title('Consensus Latency')
plt.xticks(rotation=45, ha="right")
plt.xlabel('Tests')
plt.ylabel('Latency')

# Plot for end_to_end_tps
plt.subplot(2, 2, 3)
plt.plot(df_clean['title'], df_clean['end_to_end_tps'], marker='o', color='green')
plt.title('End-to-End TPS')
plt.xticks(rotation=45, ha="right")
plt.xlabel('Tests')
plt.ylabel('TPS')

# Plot for end_to_end_latency
plt.subplot(2, 2, 4)
plt.plot(df_clean['title'], df_clean['end_to_end_latency'], marker='o', color='red')
plt.title('End-to-End Latency')
plt.xticks(rotation=45, ha="right")
plt.xlabel('Tests')
plt.ylabel('Latency')

plt.tight_layout()
plt.show()