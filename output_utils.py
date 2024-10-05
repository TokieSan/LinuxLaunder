from typing import List, Tuple

VERBOSE = False
QUIET = False
HIDE_DEEP_FILES = False

def set_output_mode(verbose: bool, quiet: bool, hide_deep_files: bool):
    global VERBOSE, QUIET, HIDE_DEEP_FILES
    VERBOSE = verbose
    QUIET = quiet
    HIDE_DEEP_FILES = hide_deep_files

def print_verbose(message):
    if VERBOSE and not QUIET:
        print(message)

def print_quiet(message):
    if not QUIET:
        print(message)

def format_size(size_in_bytes: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} PB"

def print_list(items: List[Tuple[str, int, str, int]], threshold: int, item_type: str, max_depth: int):
    print_quiet(f"\nLarge {item_type}s:")
    for item, size, item_subtype, depth in items:
        if size > threshold * 1024 * 1024 and (not HIDE_DEEP_FILES or depth <= max_depth):  # Convert MB to bytes
            print_quiet(f"{item} ({item_subtype}): {format_size(size)}")

def print_folders(folders: List[Tuple[str, int]], threshold: int):
    print_quiet("\nLarge folders:")
    for folder, size in folders:
        if size > threshold * 1024 * 1024:  # Convert MB to bytes
            print_quiet(f"{folder}: {format_size(size)}")

def print_packages(packages: List[Tuple[str, int]], threshold: int):
    print_quiet("\nLarge packages:")
    for package, size in packages:
        if size > threshold * 1024:  # Package sizes are in KB
            print_quiet(f"{package}: {format_size(size * 1024)}")  # Convert KB to bytes for consistent formatting
