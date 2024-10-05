import os
import time
import concurrent.futures
from typing import List, Tuple
from file_utils import get_file_size, is_media_file, is_document_file, is_archive_file, is_temporary_file, is_package_file, is_potentially_malicious
from folder_utils import get_folder_size
from output_utils import print_verbose, print_quiet

file_info_cache = {}

def process_file(file_path: str, scan_type: str, depth: int, max_depth: int) -> Tuple[str, int, str, int]:
    if file_path in file_info_cache:
        return file_info_cache[file_path]

    print_verbose(f"Processing file: {file_path}")
    file_size = get_file_size(file_path)
    file_type = 'other'
    if scan_type == 'all':
        if is_media_file(file_path):
            file_type = 'media'
        elif is_document_file(file_path):
            file_type = 'document'
        elif is_archive_file(file_path):
            file_type = 'archive'
        elif is_temporary_file(file_path):
            file_type = 'temporary'
        elif is_package_file(file_path):
            file_type = 'package'
        elif is_potentially_malicious(file_path):
            file_type = 'malicious'
    elif scan_type == 'media' and is_media_file(file_path):
        file_type = 'media'
    elif scan_type == 'document' and is_document_file(file_path):
        file_type = 'document'
    elif scan_type == 'archive' and is_archive_file(file_path):
        file_type = 'archive'
    elif scan_type == 'temporary' and is_temporary_file(file_path):
        file_type = 'temporary'
    elif scan_type == 'package' and is_package_file(file_path):
        file_type = 'package'
    elif scan_type == 'malicious' and is_potentially_malicious(file_path):
        file_type = 'malicious'
    
    result = (file_path, file_size, file_type, depth)
    file_info_cache[file_path] = result
    return result

def process_folder(folder_path: str, max_depth: int) -> Tuple[str, int]:
    print_verbose(f"Processing folder: {folder_path}")
    return (folder_path, get_folder_size(folder_path, max_depth))

def scan_directory(directory: str, ignore_list: List[str], scan_type: str, max_depth: int) -> Tuple[List[Tuple[str, int, str, int]], List[Tuple[str, int]]]:
    print_quiet(f"Starting scan of directory: {directory}")
    start_time = time.time()
    large_files = []
    large_folders = []
    
    with concurrent.futures.ProcessPoolExecutor() as executor:
        file_futures = []
        folder_futures = []
        
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in ignore_list]
            depth = root[len(directory):].count(os.sep)
            
            if depth <= max_depth:
                for file in files:
                    file_path = os.path.join(root, file)
                    future = executor.submit(process_file, file_path, scan_type, depth, max_depth)
                    file_futures.append(future)
            
            for d in dirs:
                folder_path = os.path.join(root, d)
                future = executor.submit(process_folder, folder_path, max_depth - depth)
                folder_futures.append(future)

        total_files = len(file_futures)
        total_folders = len(folder_futures)
        print_quiet(f"Total files to process: {total_files}")
        print_quiet(f"Total folders to process: {total_folders}")

        for i, future in enumerate(concurrent.futures.as_completed(file_futures), 1):
            result = future.result()
            if result[2] != 'other':
                large_files.append(result)
            if i % 1000 == 0:
                print_verbose(f"Processed {i}/{total_files} files")

        for i, future in enumerate(concurrent.futures.as_completed(folder_futures), 1):
            large_folders.append(future.result())
            if i % 100 == 0:
                print_verbose(f"Processed {i}/{total_folders} folders")

    end_time = time.time()
    print_quiet(f"Scan completed in {end_time - start_time:.2f} seconds")

    return (sorted(large_files, key=lambda x: x[1], reverse=True),
            sorted(large_folders, key=lambda x: x[1], reverse=True))
