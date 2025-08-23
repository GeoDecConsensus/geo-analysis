import pandas as pd
import numpy as np
import time
from pre_processing.gdi_calculator import GDI_Calculator
import os

def create_test_data(n_validators=100):
    """Create test data for performance comparison."""
    np.random.seed(42)
    
    data = []
    for i in range(n_validators):
        data.append({
            'uuid': f'validator_{i:04d}',
            'latitude': np.random.uniform(-60, 60),
            'longitude': np.random.uniform(-150, 150),
            'stake_weight': np.random.exponential(1) + 0.1
        })
    
    df = pd.DataFrame(data)
    df['stake_weight'] = df['stake_weight'] / df['stake_weight'].sum()
    return df

def test_with_projections():
    """Test measurable sizes and project to larger ones."""
    # Measured sizes
    measured_sizes = [10, 100, 200, 1000, 10000]
    # Projected sizes  
    projected_sizes = [100000, 1000000]
    
    print("GDI Distance Matrix Performance Test with Projections")
    print("=" * 60)
    
    measured_results = []
    
    # Run actual measurements
    for n in measured_sizes:
        print(f"\nTesting {n:,} validators...")
        
        try:
            # Create test data
            start_data = time.time()
            df = create_test_data(n)
            data_time = time.time() - start_data
            
            # Time the distance matrix computation
            start_time = time.time()
            calculator = GDI_Calculator(df)
            distance_time = time.time() - start_time
            
            # Calculate memory usage estimate (in GB)
            memory_gb = (n * n * 8) / (1024**3)
            
            result = {
                'n_validators': n,
                'data_generation_time': data_time,
                'distance_matrix_time': distance_time,
                'total_time': data_time + distance_time,
                'time_per_validator_ms': (distance_time / n) * 1000,
                'estimated_memory_gb': memory_gb,
                'measurement_type': 'measured'
            }
            
            measured_results.append(result)
            
            print(f"  Distance matrix: {distance_time:.3f}s")
            print(f"  Total time: {data_time + distance_time:.3f}s")
            print(f"  Per validator: {(distance_time/n)*1000:.3f}ms")
            print(f"  Memory: {memory_gb:.2f} GB")
            
        except Exception as e:
            print(f"  Error: {e}")
            break
    
    # Project to larger sizes based on O(n²) scaling
    all_results = measured_results.copy()
    
    if len(measured_results) >= 2:
        # Use largest measurement for scaling factor
        largest = measured_results[-1]
        scaling_factor = largest['distance_matrix_time'] / (largest['n_validators'] ** 2)
        
        print(f"\nProjecting to larger sizes using O(n²) scaling...")
        print(f"Scaling factor: {scaling_factor:.2e} s/validator²")
        
        for n in projected_sizes:
            projected_time = n ** 2 * scaling_factor
            projected_memory = (n * n * 8) / (1024**3)
            
            result = {
                'n_validators': n,
                'data_generation_time': 0,  # Projected
                'distance_matrix_time': projected_time,
                'total_time': projected_time,
                'time_per_validator_ms': (projected_time / n) * 1000,
                'estimated_memory_gb': projected_memory,
                'measurement_type': 'projected'
            }
            
            all_results.append(result)
            
            if projected_time < 3600:
                time_str = f"{projected_time:.1f}s"
            elif projected_time < 86400:
                time_str = f"{projected_time/3600:.1f}h"
            else:
                time_str = f"{projected_time/86400:.1f}d"
                
            print(f"\n  {n:,} validators (projected):")
            print(f"    Distance matrix: {time_str}")
            print(f"    Memory: {projected_memory:.1f} GB")
            print(f"    Per validator: {(projected_time/n)*1000:.3f}ms")
    
    return all_results

if __name__ == "__main__":
    results = test_with_projections()
    
    if results:
        results_df = pd.DataFrame(results)
        
        # Create data directory and save
        os.makedirs('data', exist_ok=True)
        output_file = 'data/gdi_complexity.csv'
        results_df.to_csv(output_file, index=False)
        
        print(f"\n" + "=" * 60)
        print(f"RESULTS SAVED TO: {output_file}")
        print("=" * 60)
        
        # Print comprehensive summary
        print("\nCOMPREHENSIVE PERFORMANCE SUMMARY:")
        print("-" * 60)
        print("Validators | Type      | Time      | Memory   | Per-Val")
        print("-" * 60)
        
        for _, row in results_df.iterrows():
            n = int(row['n_validators'])
            time_val = row['distance_matrix_time']
            memory = row['estimated_memory_gb']
            per_val = row['time_per_validator_ms']
            mtype = row['measurement_type']
            
            if time_val < 60:
                time_str = f"{time_val:.2f}s"
            elif time_val < 3600:
                time_str = f"{time_val/60:.1f}m"
            elif time_val < 86400:
                time_str = f"{time_val/3600:.1f}h"
            else:
                time_str = f"{time_val/86400:.1f}d"
            
            if memory < 1:
                mem_str = f"{memory*1024:.0f}MB"
            elif memory < 1024:
                mem_str = f"{memory:.1f}GB"
            else:
                mem_str = f"{memory/1024:.1f}TB"
                
            print(f"{n:>9,} | {mtype:<9} | {time_str:>8} | {mem_str:>7} | {per_val:>6.2f}ms")
        
        print("-" * 60)
        print("Legend: s=seconds, m=minutes, h=hours, d=days")
        
        # Highlight key findings
        print(f"\nKEY FINDINGS:")
        print("-" * 60)
        result_10k = results_df[results_df['n_validators'] == 10000].iloc[0]
        result_1M = results_df[results_df['n_validators'] == 1000000].iloc[0]
        
        print(f"✅ 10,000 validators (Ethereum scale):")
        print(f"   Time: {result_10k['distance_matrix_time']:.1f}s")
        print(f"   Memory: {result_10k['estimated_memory_gb']:.1f}GB")
        print(f"   Assessment: HIGHLY PRACTICAL")
        
        print(f"\n🔮 1,000,000 validators (projected):")
        if result_1M['distance_matrix_time'] < 3600:
            print(f"   Time: {result_1M['distance_matrix_time']:.0f}s ({result_1M['distance_matrix_time']/60:.1f}m)")
        else:
            print(f"   Time: {result_1M['distance_matrix_time']/3600:.1f}h")
        print(f"   Memory: {result_1M['estimated_memory_gb']:.0f}GB")
        
        if result_1M['distance_matrix_time'] < 86400:
            print(f"   Assessment: COMPUTATIONALLY FEASIBLE")
        else:
            print(f"   Assessment: REQUIRES OPTIMIZATION")