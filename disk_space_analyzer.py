 #!/usr/bin/env python3

import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple
import concurrent.futures
from functools import partial
import re
import shutil
import time

# Global variables for verbose and quiet modes
VERBOSE = False
QUIET = False
HIDE_DEEP_FILES = False

def print_verbose(message):
    if VERBOSE and not QUIET:
        print(message)

def print_quiet(message):
    if not QUIET:
        print(message)

def get_file_size(file_path: str) -> int:
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0

def get_folder_size(folder_path: str, max_depth: int, current_depth: int = 0) -> int:
    if current_depth >= max_depth:
        return 0
    total_size = 0
    print_verbose(f"Processing folder: {folder_path}")
    try:
        for item in os.scandir(folder_path):
            if item.is_file():
                total_size += item.stat().st_size
            elif item.is_dir():
                total_size += get_folder_size(item.path, max_depth, current_depth + 1)
    except PermissionError:
        print_verbose(f"Permission denied: {folder_path}")
    except OSError as e:
        print_verbose(f"Error accessing {folder_path}: {e}")
    return total_size

def is_media_file(file_path: str) -> bool:
    media_extensions = {'.mp3', '.mp4', '.avi', '.mov', '.jpg', '.jpeg', '.png', '.gif', '.wav', '.flac', '.mkv'}
    return os.path.splitext(file_path)[1].lower() in media_extensions

def is_document_file(file_path: str) -> bool:
    document_extensions = {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'}
    return os.path.splitext(file_path)[1].lower() in document_extensions

def is_archive_file(file_path: str) -> bool:
    archive_extensions = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'}
    return os.path.splitext(file_path)[1].lower() in archive_extensions

def is_temporary_file(file_path: str) -> bool:
    temp_patterns = {'.tmp', '.temp', '~', '.bak', '.swp'}
    return any(pattern in os.path.basename(file_path).lower() for pattern in temp_patterns)

def is_package_file(file_path: str) -> bool:
    package_extensions = {'.deb', '.rpm', '.tar.gz', '.apk'}
    return os.path.splitext(file_path)[1].lower() in package_extensions

def is_potentially_malicious(file_path: str) -> bool:
    suspicious_extensions = {'.exe', '.bat', '.sh', '.vbs', '.js'}
    return os.path.splitext(file_path)[1].lower() in suspicious_extensions

def process_file(file_path: str, scan_type: str, depth: int, max_depth: int) -> Tuple[str, int, str, int]:
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
    return (file_path, file_size, file_type, depth)

def process_folder(folder_path: str, max_depth: int) -> Tuple[str, int]:

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

def parse_size(size_str: str) -> int:
    size_str = size_str.lower()
    if 'kib' in size_str:
        return int(float(size_str.replace('kib', '').strip()))
    elif 'mib' in size_str:
        return int(float(size_str.replace('mib', '').strip()) * 1024)
    elif 'gib' in size_str:
        return int(float(size_str.replace('gib', '').strip()) * 1024 * 1024)
    elif 'kb' in size_str:
        return int(float(size_str.replace('kb', '').strip()))
    elif 'mb' in size_str:
        return int(float(size_str.replace('mb', '').strip()) * 1024)
    elif 'gb' in size_str:
        return int(float(size_str.replace('gb', '').strip()) * 1024 * 1024)
    else:
        return int(float(size_str))  # Assume it's already in KB

def get_installed_packages(distro: str) -> List[Tuple[str, int]]:
    print_quiet("Retrieving installed packages...")
    if distro == 'arch':
        cmd = "pacman -Qi | awk '/^Name/{name=$3} /^Installed Size/{size=$4$5; print name, size}'"
    elif distro == 'ubuntu':
        cmd = "dpkg-query -W -f='${Package} ${Installed-Size}\n'"
    else:
        raise ValueError(f"Unsupported distribution: {distro}")

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    packages = []
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            name = parts[0]
            size_str = ' '.join(parts[1:])
            try:
                size = parse_size(size_str)
                packages.append((name, size))
            except ValueError:
                print(f"Warning: Could not parse size for package {name}: {size_str}")
    return sorted(packages, key=lambda x: x[1], reverse=True)

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

def remove_file(file_path: str):
    try:
        os.remove(file_path)
        print_quiet(f"Deleted file: {file_path}")
    except OSError as e:
        print_quiet(f"Error deleting file {file_path}: {e}")

def remove_folder(folder_path: str):
    try:
        shutil.rmtree(folder_path)
        print_quiet(f"Deleted folder: {folder_path}")
    except OSError as e:
        print_quiet(f"Error deleting folder {folder_path}: {e}")

def uninstall_package(package: str, distro: str):
    if distro == 'arch':
        cmd = ['sudo', 'pacman', '-R', package]
    elif distro == 'ubuntu':
        cmd = ['sudo', 'apt', 'remove', package]
    else:
        print_quiet(f"Unsupported distribution: {distro}")
        return

    try:
        subprocess.run(cmd, check=True)
        print_quiet(f"Uninstalled package: {package}")
    except subprocess.CalledProcessError as e:
        print_quiet(f"Error uninstalling package {package}: {e}")

def main():
    global VERBOSE, QUIET, HIDE_DEEP_FILES
    parser = argparse.ArgumentParser(description="Enhanced Disk Space Analyzer")
    parser.add_argument("--directory", "-d", default="/", help="Directory to scan")
    parser.add_argument("--ignore", "-i", nargs="+", default=[], help="Directories to ignore")
    parser.add_argument("--scan-type", "-s", choices=['all', 'media', 'document', 'archive', 'temporary', 'package', 'malicious'], default='all', help="Type of files to scan")
    parser.add_argument("--distro", choices=['arch', 'ubuntu'], default='arch', help="Linux distribution")
    parser.add_argument("--threshold", "-t", type=int, default=100, help="Size threshold in MB")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--quiet", "-q", action="store_true", help="Enable quiet mode (suppresses all output except results)")
    parser.add_argument("--max-depth", type=int, default=4, help="Maximum depth for subfolder size checking")
    parser.add_argument("--hide-deep-files", action="store_true", help="Hide files in directories beyond max depth")
    args = parser.parse_args()

    VERBOSE = args.verbose
    QUIET = args.quiet
    HIDE_DEEP_FILES = args.hide_deep_files

    if VERBOSE and QUIET:
        print("Error: Cannot use both verbose and quiet modes simultaneously.")
        sys.exit(1)

    print_quiet(f"Scanning directory: {args.directory}")
    print_quiet(f"Ignore list: {args.ignore}")
    print_quiet(f"Scan type: {args.scan_type}")
    print_quiet(f"Distribution: {args.distro}")
    print_quiet(f"Threshold: {args.threshold} MB")
    print_quiet(f"Max depth: {args.max_depth}")
    print_quiet(f"Hide deep files: {HIDE_DEEP_FILES}")

    large_files, large_folders = scan_directory(args.directory, args.ignore, args.scan_type, args.max_depth)
    large_packages = get_installed_packages(args.distro)

    print_list(large_files, args.threshold, "file", args.max_depth)
    print_folders(large_folders, args.threshold)
    print_packages(large_packages, args.threshold)

    while True:
        print_quiet("\nOptions:")
        print_quiet("1. Remove a file")
        print_quiet("2. Remove a folder")
        print_quiet("3. Uninstall a package")
        print_quiet("4. Exit")
        
        choice = input("Enter your choice (1-4): ").strip()
 
        if choice == '1':
            file_path = input("Enter the path of the file to remove: ").strip()
            if os.path.isfile(file_path):
                remove_file(file_path)
            else:
                print_quiet("Invalid file path.")
        elif choice == '2':
            folder_path = input("Enter the path of the folder to remove: ").strip()
            if os.path.isdir(folder_path):
                remove_folder(folder_path)
            else:
                print_quiet("Invalid folder path.")
        elif choice == '3':
            package_name = input("Enter the name of the package to uninstall: ").strip()
            uninstall_package(package_name, args.distro)
        elif choice == '4':
            print_quiet("Exiting the program.")
            break
        else:
            print_quiet("Invalid choice. Please enter a number between 1 and 4.")

if __name__ == "__main__":
    main()
