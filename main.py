#!/usr/bin/env python3

import argparse
import sys
import os
import curses
from scan_utils import run_scan
from package_utils import get_installed_packages, uninstall_package
from output_utils import print_list, print_folders, print_packages, print_quiet, set_output_mode, format_size
from file_utils import remove_file
from folder_utils import remove_folder

class TreeNode:
    def __init__(self, name, path, size, is_file=False):
        self.name = name
        self.path = path
        self.size = size
        self.is_file = is_file
        self.children = []
        self.expanded = False
        self.selected = False

def build_folder_tree(items):
    root = TreeNode("", "", 0)
    nodes = {"": root}  # Use empty string as key for root

    # Create a dictionary of sizes from items
    size_dict = {path: size for path, size, _ in items}
    # print(size_dict)


    # Build the tree
    for path, size, item_type in items:
        parts = path.split(os.sep)
        current_path = ""
        for part in parts:
            prev_path = current_path
            current_path = os.path.join(current_path, part)
            if current_path not in nodes:
                parent = nodes[prev_path]
                proper_path = '/' + current_path
                if not size_dict.get(proper_path):
                    proper_path = proper_path + '/'
                new_node = TreeNode(part, current_path, size_dict.get(proper_path, 0), item_type != 'folder')
                parent.children.append(new_node)
                nodes[current_path] = new_node

    # Sort children of each node by size
    def sort_children(node):
        node.children.sort(key=lambda x: x.size, reverse=True)
        for child in node.children:
            sort_children(child)

    sort_children(root)
    return root

def flatten_folder_tree(node, prefix="", depth=0):
    flat_list = []
    if node.name:
        if node.selected:
            expander = "x"
        elif node.children:
            expander = "-" if node.expanded else "+"
        else:
            expander = " "
        flat_list.append((f"{prefix}[{expander}] {node.name}", node, depth))
    if node.expanded or not node.name:
        for child in node.children:
            flat_list.extend(flatten_folder_tree(child, prefix + "│   ", depth + 1))
    return flat_list

def interactive_selection(stdscr, root_node, title):
    curses.curs_set(0)
    stdscr.clear()
    
    current_idx = 0
    start_idx = 0
    
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        stdscr.addstr(0, 0, title, curses.A_BOLD)
        stdscr.addstr(1, 0, "Use arrow keys to navigate, Enter to expand/collapse, Space to select/deselect, 'q' to confirm")
        
        flat_list = flatten_folder_tree(root_node)
        
        for idx, (item_str, node, depth) in enumerate(flat_list[start_idx:start_idx+height-3]):
            if start_idx + idx == current_idx:
                stdscr.addstr(idx+2, 0, "> ", curses.A_BOLD)
            else:
                stdscr.addstr(idx+2, 0, "  ")
            
            display_str = f"{item_str} ({format_size(node.size)})"
            if len(display_str) > width - 3:
                display_str = display_str[:width-6] + "..."
            stdscr.addstr(idx+2, 2, display_str)
        
        stdscr.refresh()
        
        key = stdscr.getch()
        if key == ord('q'):
            return [node.path for _, node, _ in flat_list if node.selected]
        elif key == ord(' '):
            current_node = flat_list[current_idx][1]
            current_node.selected = not current_node.selected
            # Propagate selection to children
            def toggle_children(node, state):
                for child in node.children:
                    child.selected = state
                    toggle_children(child, state)
            toggle_children(current_node, current_node.selected)
        elif key == 10:  # Enter key
            if flat_list[current_idx][1].children:
                flat_list[current_idx][1].expanded = not flat_list[current_idx][1].expanded
        elif key == curses.KEY_UP and current_idx > 0:
            current_idx -= 1
            if current_idx < start_idx:
                start_idx = current_idx
        elif key == curses.KEY_DOWN and current_idx < len(flat_list) - 1:
            current_idx += 1
            if current_idx >= start_idx + height - 3:
                start_idx = current_idx - (height - 4)

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

    large_files, large_folders = run_scan(args.directory, args.ignore, args.scan_type, args.max_depth)

    print_list(large_files, args.threshold, "file")
    print_folders(large_folders, args.threshold)
    large_packages = get_installed_packages(args.distro)
    print_packages(large_packages, args.threshold)

    large_files = [x for x in large_files if x[1] == 0]

    while True:
        print_quiet("\nOptions:")
        print_quiet("1. Remove files and folders")
        print_quiet("2. Uninstall packages")
        print_quiet("3. Exit")
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == '1':
            items = [(f[0], f[1], f[2]) for f in large_files if f[1] > args.threshold * 1024 * 1024] + \
                    [(f[0], f[1], 'folder') for f in large_folders if f[1] > args.threshold * 1024 * 1024]
            root_node = build_folder_tree(items)
            items_to_remove = curses.wrapper(interactive_selection, root_node.children[0].children[0], "Select files and folders to remove")
            for item_path in items_to_remove:
                if os.path.isfile(item_path):
                    remove_file(item_path)
                elif os.path.isdir(item_path):
                    remove_folder(item_path)
        elif choice == '2':
            packages_root = TreeNode("", "", 0)
            for package, size in sorted(large_packages, key=lambda x: x[1], reverse=True):
                if size > args.threshold * 1024:  # size is in KB, threshold is in MB
                    packages_root.children.append(TreeNode(package, package, size * 1024, True))
            packages_root.children.sort(key=lambda x: x.size, reverse=True)
            packages_to_remove = curses.wrapper(interactive_selection, packages_root, "Select packages to uninstall")
            for package_name in packages_to_remove:
                uninstall_package(package_name, args.distro)
        elif choice == '3':
            print_quiet("Exiting the program.")
            break
        else:
            print_quiet("Invalid choice. Please enter a number between 1 and 3.")

if __name__ == "__main__":
    main()
