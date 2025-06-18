import os
import pandas as pd
from datetime import datetime
import time
from multiprocessing import Pool, cpu_count
from functools import partial

def check_file_modtime(file_path, cutoff_date):
    """Check if file's modification time is before cutoff date"""
    mod_time = os.path.getmtime(file_path)
    mod_datetime = datetime.fromtimestamp(mod_time)
    return mod_datetime < cutoff_date
def process_single_directory(args):
    """Process a single directory for target files"""
    root, target_files, cutoff_date = args
    old_files = []
    
    # Only process directories that contain 'nocarb' in their path
    if 'nocarb' not in root:
        return old_files
        
    # Only process the smallest directories (those with no subdirectories)
    if any(os.path.isdir(os.path.join(root, d)) for d in os.listdir(root)):
        return old_files
        
    for file in os.listdir(root):
        if file in target_files and file.endswith('.csv'):
            file_path = os.path.join(root, file)
            if check_file_modtime(file_path, cutoff_date):
                old_files.append({
                    'file_name': file,
                    'directory': root,
                    'last_modified': datetime.fromtimestamp(os.path.getmtime(file_path))
                })
    
    return old_files

def get_all_directories(base_dir):
    """Get all directories that need to be processed"""
    directories = []
    for root, dirs, files in os.walk(base_dir):
        if 'nocarb' in root and not any(os.path.isdir(os.path.join(root, d)) for d in dirs):
            directories.append(root)
    return directories

def main():
    # Define base directories
    base_dirs = [
        r'C:\Users\jiahuic\University of Michigan Dropbox\Jiahui Chen\Ford_CC\Result_v2h',
        r'C:\Users\jiahuic\University of Michigan Dropbox\Jiahui Chen\Ford_CC\Result_v2h_no',
        r'C:\Users\jiahuic\University of Michigan Dropbox\Jiahui Chen\Ford_CC\Result_cc',
    ]
    
    # Define cutoff date (May 1st, 2024)
    cutoff_date = datetime(2025, 5, 1)
    
    # Get list of target files
    target_files = os.listdir(r'C:\Users\jiahuic\University of Michigan Dropbox\Jiahui Chen\Ford_CC\Result_v2h\Results_80_Y60_2024_cons_nocarb\0_0_0')[:15]
    
    # Get all directories to process
    all_directories = []
    for base_dir in base_dirs:
        if os.path.exists(base_dir):
            all_directories.extend(get_all_directories(base_dir))
    
    # Prepare arguments for parallel processing
    process_args = [(dir_path, target_files, cutoff_date) for dir_path in all_directories]
    
    # Use parallel processing to check files
    num_processes = max(1, cpu_count() - 1)  # Leave one CPU free
    with Pool(processes=num_processes) as pool:
        results = pool.map(process_single_directory, process_args)
    
    # Flatten results
    all_old_files = [item for sublist in results for item in sublist]
    
    # Create DataFrame and save to CSV
    if all_old_files:
        df = pd.DataFrame(all_old_files)
        output_path = 'old_files_report.csv'
        df.to_csv(output_path, index=False)
        print(f"Found {len(all_old_files)} files modified before May 2024")
        print(f"Report saved to {output_path}")
    else:
        print("No old files found")

if __name__ == '__main__':
    main()
