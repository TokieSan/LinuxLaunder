import os
import shutil
from output_utils import print_verbose, print_quiet

folder_size_cache = {}

def get_folder_size(folder_path: str, max_depth: int) -> int:
    if max_depth <= 0:
        return 0

    cache_key = (folder_path, max_depth)
    if cache_key in folder_size_cache:
        return folder_size_cache[cache_key]

    total_size = 0
    try:
        with os.scandir(folder_path) as entries:
            for entry in entries:
                try:
                    if entry.is_file(follow_symlinks=False):
                        total_size += entry.stat(follow_symlinks=False).st_size
                    elif entry.is_dir(follow_symlinks=False):
                        total_size += get_folder_size(entry.path, max_depth - 1)
                except PermissionError:
                    print_verbose(f"Permission denied: {entry.path}")
                except OSError as e:
                    print_verbose(f"Error accessing {entry.path}: {e}")
    except PermissionError:
        print_verbose(f"Permission denied: {folder_path}")
    except OSError as e:
        print_verbose(f"Error accessing {folder_path}: {e}")

    folder_size_cache[cache_key] = total_size
    return total_size

def calculate_folder_sizes(root_path: str, max_depth: int) -> dict:
    folder_sizes = {}
    for current_path, dirs, files in os.walk(root_path, topdown=True):
        current_depth = current_path[len(root_path):].count(os.sep)
        if current_depth > max_depth:
            dirs[:] = []  # Don't recurse further
            continue
        
        folder_size = sum(
            os.path.getsize(os.path.join(current_path, file))
            for file in files
            if os.path.isfile(os.path.join(current_path, file))
        )
        folder_sizes[current_path] = folder_size

    # Calculate cumulative sizes
    for folder in sorted(folder_sizes.keys(), key=len, reverse=True):
        parent = os.path.dirname(folder)
        if parent in folder_sizes:
            folder_sizes[parent] += folder_sizes[folder]

    return folder_sizes

def remove_folder(folder_path: str):
    try:
        shutil.rmtree(folder_path)
        print_quiet(f"Deleted folder: {folder_path}")
    except OSError as e:
        print_quiet(f"Error deleting folder {folder_path}: {e}")
