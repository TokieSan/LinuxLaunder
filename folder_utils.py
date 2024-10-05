import os
import shutil
from file_utils import get_file_size
from output_utils import print_verbose, print_quiet

folder_size_cache = {}

def get_folder_size(folder_path: str, max_depth: int, current_depth: int = 0) -> int:
    if current_depth >= max_depth:
        return 0
    
    cache_key = (folder_path, max_depth - current_depth)
    if cache_key in folder_size_cache:
        return folder_size_cache[cache_key]
    
    total_size = 0
    try:
        for item in os.scandir(folder_path):
            if item.is_file():
                total_size += get_file_size(item.path)
            elif item.is_dir():
                total_size += get_folder_size(item.path, max_depth, current_depth + 1)
    except PermissionError:
        print_verbose(f"Permission denied: {folder_path}")
    except OSError as e:
        print_verbose(f"Error accessing {folder_path}: {e}")
    
    folder_size_cache[cache_key] = total_size
    return total_size

def remove_folder(folder_path: str):
    try:
        shutil.rmtree(folder_path)
        print_quiet(f"Deleted folder: {folder_path}")
    except OSError as e:
        print_quiet(f"Error deleting folder {folder_path}: {e}")
