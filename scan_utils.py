import os
import time
import asyncio
import concurrent.futures
from typing import List, Tuple, Dict
from file_utils import is_media_file, is_document_file, is_archive_file, is_temporary_file, is_package_file, is_potentially_malicious
from output_utils import print_verbose, print_quiet

file_info_cache: Dict[str, Tuple[float, int]] = {}
folder_size_cache: Dict[str, Tuple[float, int]] = {}

async def get_file_info(file_path: str, scan_type: str) -> Tuple[str, int, str]:
    try:
        stat = os.stat(file_path)
        file_size = stat.st_size
        mtime = stat.st_mtime

        if file_path in file_info_cache:
            cached_mtime, cached_size = file_info_cache[file_path]
            if mtime == cached_mtime:
                return file_path, cached_size, 'cached'

        file_type = 'other'
        if scan_type == 'all':
            if await asyncio.to_thread(is_media_file, file_path):
                file_type = 'media'
            elif await asyncio.to_thread(is_document_file, file_path):
                file_type = 'document'
            elif await asyncio.to_thread(is_archive_file, file_path):
                file_type = 'archive'
            elif await asyncio.to_thread(is_temporary_file, file_path):
                file_type = 'temporary'
            elif await asyncio.to_thread(is_package_file, file_path):
                file_type = 'package'
            elif await asyncio.to_thread(is_potentially_malicious, file_path):
                file_type = 'malicious'
        elif scan_type == 'media' and await asyncio.to_thread(is_media_file, file_path):
            file_type = 'media'
        elif scan_type == 'document' and await asyncio.to_thread(is_document_file, file_path):
            file_type = 'document'
        elif scan_type == 'archive' and await asyncio.to_thread(is_archive_file, file_path):
            file_type = 'archive'
        elif scan_type == 'temporary' and await asyncio.to_thread(is_temporary_file, file_path):
            file_type = 'temporary'
        elif scan_type == 'package' and await asyncio.to_thread(is_package_file, file_path):
            file_type = 'package'
        elif scan_type == 'malicious' and await asyncio.to_thread(is_potentially_malicious, file_path):
            file_type = 'malicious'

        file_info_cache[file_path] = (mtime, file_size)
        return file_path, file_size, file_type
    except (FileNotFoundError, PermissionError):
        return file_path, 0, 'error'

async def scan_directory(directory: str, ignore_list: List[str], scan_type: str, max_depth: int) -> Tuple[List[Tuple[str, int, str]], List[Tuple[str, int]]]:
    print_quiet(f"Starting scan of directory: {directory}")
    start_time = time.time()
    
    large_files = []
    large_folders = []
    
    async def process_directory(dir_path: str, depth: int):
        nonlocal large_files, large_folders
        if depth > max_depth:
            return 0
        
        try:
            dir_stat = os.stat(dir_path)
            dir_mtime = dir_stat.st_mtime
            if dir_path in folder_size_cache:
                cached_mtime, cached_size = folder_size_cache[dir_path]
                if dir_mtime == cached_mtime:
                    large_folders.append((dir_path, cached_size))
                    return cached_size

            total_size = 0
            file_tasks = []
            for entry in os.scandir(dir_path):
                if entry.name in ignore_list:
                    continue
                if entry.is_file(follow_symlinks=False):
                    file_tasks.append(get_file_info(entry.path, scan_type))
                elif entry.is_dir(follow_symlinks=False):
                    total_size += await process_directory(entry.path, depth + 1)

            file_results = await asyncio.gather(*file_tasks)
            for file_path, file_size, file_type in file_results:
                total_size += file_size
                if file_type not in ['other', 'error', 'cached']:
                    large_files.append((file_path, file_size, file_type))

            large_folders.append((dir_path, total_size))
            folder_size_cache[dir_path] = (dir_mtime, total_size)
            return total_size
        except (PermissionError, FileNotFoundError):
            print_verbose(f"Error accessing {dir_path}")
            return 0

    await process_directory(directory, 0)

    end_time = time.time()
    print_quiet(f"Scan completed in {end_time - start_time:.2f} seconds")

    return (sorted(large_files, key=lambda x: x[1], reverse=True),
            sorted(large_folders, key=lambda x: x[1], reverse=True))

def run_scan(directory: str, ignore_list: List[str], scan_type: str, max_depth: int) -> Tuple[List[Tuple[str, int, str]], List[Tuple[str, int]]]:
    return asyncio.run(scan_directory(directory, ignore_list, scan_type, max_depth))
