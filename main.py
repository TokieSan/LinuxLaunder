#!/usr/bin/env python3

import argparse
import sys
import os
import curses
from scan_utils import scan_directory
from package_utils import get_installed_packages, uninstall_package
from output_utils import print_list, print_folders, print_packages, print_quiet, set_output_mode, format_size
from file_utils import remove_file
from folder_utils import remove_folder

def build_folder_tree(folders):
    tree = {}
    for folder, size in folders:
        parts = folder.split(os.sep)
        current = tree
        for part in parts:
            if part not in current:
                current[part] = {"__size__": size, "__path__": folder}
            current = current[part]
    return tree

def flatten_folder_tree(tree, prefix="", depth=0):
    flat_list = []
    for key, value in sorted(tree.items()):
        if key != "__size__" and key != "__path__":
            size = value["__size__"]
            path = value["__path__"]
            flat_list.append((f"{prefix}{'  ' * depth}├─ {key}", path, size))
            flat_list.extend(flatten_folder_tree(value, prefix + "│  ", depth + 1))
    return flat_list

def interactive_selection(stdscr, items, title):
    curses.curs_set(0)
    stdscr.clear()
    
    selected = [False] * len(items)
    current_idx = 0
    start_idx = 0
    
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        stdscr.addstr(0, 0, title, curses.A_BOLD)
        stdscr.addstr(1, 0, "Use arrow keys to navigate, Space to select/deselect, Enter to confirm")
        
        for idx, item in enumerate(items[start_idx:start_idx+height-3]):
            if start_idx + idx == current_idx:
                stdscr.addstr(idx+2, 0, "> ", curses.A_BOLD)
            else:
                stdscr.addstr(idx+2, 0, "  ")
            
            checkbox = "[x]" if selected[start_idx + idx] else "[ ]"
            if isinstance(item, tuple):  # For files and folders
                item_str = f"{checkbox} {item[0]} ({format_size(item[2])})"
            else:  # For packages
                item_str = f"{checkbox} {item}"
            if len(item_str) > width - 3:
                item_str = item_str[:width-6] + "..."
            stdscr.addstr(idx+2, 2, item_str)
        
        stdscr.refresh()
        
        key = stdscr.getch()
        if key == ord('q'):
            return []
        elif key == ord(' '):
            selected[current_idx] = not selected[current_idx]
        elif key == curses.KEY_UP and current_idx > 0:
            current_idx -= 1
            if current_idx < start_idx:
                start_idx = current_idx
        elif key == curses.KEY_DOWN and current_idx < len(items) - 1:
            current_idx += 1
            if current_idx >= start_idx + height - 3:
                start_idx = current_idx - (height - 4)
        elif key == 10:  # Enter key
            return [item[1] if isinstance(item, tuple) else item for item, sel in zip(items, selected) if sel]

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
        print_quiet("1. Remove files")
        print_quiet("2. Remove folders")
        print_quiet("3. Uninstall packages")
        print_quiet("4. Exit")
        
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == '1':
            files_to_show = [(f[0], f[0], f[1]) for f in large_files if f[1] > args.threshold * 1024 * 1024]
            files_to_remove = curses.wrapper(interactive_selection, files_to_show, "Select files to remove")
            for file_path in files_to_remove:
                remove_file(file_path)
        elif choice == '2':
            folder_tree = build_folder_tree([(f[0], f[1]) for f in large_folders if f[1] > args.threshold * 1024 * 1024])
            folders_to_show = flatten_folder_tree(folder_tree)
            folders_to_remove = curses.wrapper(interactive_selection, folders_to_show, "Select folders to remove")
            for folder_path in folders_to_remove:
                remove_folder(folder_path)
        elif choice == '3':
            packages_to_remove = curses.wrapper(interactive_selection, [p[0] for p in large_packages if p[1] > args.threshold * 1024], "Select packages to uninstall")
            for package_name in packages_to_remove:
                uninstall_package(package_name, args.distro)
        elif choice == '4':
            print_quiet("Exiting the program.")
            break
        else:
            print_quiet("Invalid choice. Please enter a number between 1 and 4.")

if __name__ == "__main__":
    main()
