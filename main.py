#!/usr/bin/env python3

import argparse
import sys
import os
from scan_utils import scan_directory
from package_utils import get_installed_packages, uninstall_package
from output_utils import print_list, print_folders, print_packages, print_quiet, set_output_mode
from file_utils import remove_file
from folder_utils import remove_folder

def main():
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

    if args.verbose and args.quiet:
        print("Error: Cannot use both verbose and quiet modes simultaneously.")
        sys.exit(1)

    set_output_mode(args.verbose, args.quiet, args.hide_deep_files)

    print_quiet(f"Scanning directory: {args.directory}")
    print_quiet(f"Ignore list: {args.ignore}")
    print_quiet(f"Scan type: {args.scan_type}")
    print_quiet(f"Distribution: {args.distro}")
    print_quiet(f"Threshold: {args.threshold} MB")
    print_quiet(f"Max depth: {args.max_depth}")
    print_quiet(f"Hide deep files: {args.hide_deep_files}")

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
