import os
import pandas as pd
import numpy as np
from multiprocessing import Pool, cpu_count
import json
from pathlib import Path

# Set the directory path
base_dir = r'C:\Users\jiahuic\University of Michigan Dropbox\Jiahui Chen\Ford_CC'

def check_slowcr_vsoc(file_path):
    try:
        df = pd.read_csv(file_path)
        if 'slowCR' not in df.columns or 'vSOC' not in df.columns:
            return None
        
        # Calculate vSOC differences
        vsoc_diff = df['vSOC'].diff().fillna(0)
        
        # Only compare where slowCR is not 0
        mask = df['slowCR'] != 0
        if not any(mask):
            return None
            
        # Compare slowCR with vSOC differences only where slowCR isn't 0
        is_equal = np.isclose(df.loc[mask, 'slowCR'], vsoc_diff[mask], rtol=1e-5, atol=1e-5)
        
        if not all(is_equal):
            # Convert numpy arrays to lists for JSON serialization
            return {
                'file': str(file_path),  # Convert Path to string
                'mismatch_indices': np.where(~is_equal)[0].tolist(),
                'slowCR_values': df.loc[mask, 'slowCR'][~is_equal].values.tolist(),
                'vsoc_diff_values': vsoc_diff[mask][~is_equal].values.tolist(),
                'hour_indices': df.index[mask][~is_equal].values.tolist()
            }
        return None
    except Exception as e:
        return {'file': str(file_path), 'error': str(e)}

def process_files(file_list):
    results = []
    for file_path in file_list:
        result = check_slowcr_vsoc(file_path)
        if result:
            results.append(result)
    return results

def main():
    # Get all CSV files
    all_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.csv'):
                all_files.append(os.path.join(root, file))
    
    # Split files into chunks for parallel processing
    num_cores = cpu_count()
    chunk_size = max(1, len(all_files) // (num_cores * 4))  # Divide into more chunks than cores
    file_chunks = [all_files[i:i + chunk_size] for i in range(0, len(all_files), chunk_size)]
    
    # Process files in parallel
    with Pool(num_cores) as pool:
        chunk_results = pool.map(process_files, file_chunks)
    
    # Flatten results
    mismatches = [item for sublist in chunk_results for item in sublist]
    
    # Print results
    if mismatches:
        print("Found mismatches between slowCR and vSOC differences (only where slowCR ≠ 0):")
        for mismatch in mismatches:
            if 'error' in mismatch:
                print(f"\nError in file {mismatch['file']}:")
                print(f"Error message: {mismatch['error']}")
            else:
                print(f"\nMismatches in file {mismatch['file']}:")
                print("Hour indices with mismatches:", mismatch['hour_indices'])
                print("slowCR values:", mismatch['slowCR_values'])
                print("vSOC diff values:", mismatch['vsoc_diff_values'])
                print("Absolute differences:", 
                      [abs(s - v) for s, v in zip(mismatch['slowCR_values'], mismatch['vsoc_diff_values'])])
    else:
        print("No mismatches found between slowCR and vSOC differences in any files (where slowCR ≠ 0).")

if __name__ == '__main__':
    main()
