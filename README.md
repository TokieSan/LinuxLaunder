# LinuxLaunder: Effortlessly Clean Up Large Files and Packages on Your Linux System


LinuxLaunder is an disk space analyzer and cleanup tool for Linux systems written in python. It helps you identify and remove large files, folders, and unnecessary packages, freeing up valuable disk space.

## Features

- **Multithreaded** quickly scan directories for large files and folders
- Detect various file types: media, documents, archives, temporary files, packages, and potentially malicious files
- List installed packages and their sizes
- Interactive tree-view selection for files, folders, and packages to remove
- Customizable size threshold for reporting
- Ignore specific directories during scans
- Verbose and quiet modes for different levels of output
- Support for both Arch Linux and Ubuntu distributions

## Requirements

- Python 3.6+

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/TokieSan/LinuxLaunder.git
   cd LinuxLaunder
   ```

2. (Optional) Create and activate a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Make the main script executable:
   ```
   chmod +x linuxlaunder.sh
   ```

## Usage

Run LinuxLaunder using the shell script:

```
./linuxlaunder.sh [OPTIONS]
```

### Options

- `-d, --directory DIR`: Specify the directory to scan (default: /)
- `-i, --ignore DIR1 DIR2 ...`: Specify directories to ignore during the scan
- `-s, --scan-type TYPE`: Specify the type of scan (all, media, document, archive, temporary, package, malicious)
- `-t, --threshold SIZE`: Set the size threshold in MB for reporting large files (default: 100)
- `-v, --verbose`: Enable verbose output
- `-q, --quiet`: Enable quiet mode (suppresses all output except results)
- `--max-depth DEPTH`: Maximum depth for subfolder size checking (default: 4)
- `--hide-deep-files`: Hide files in directories beyond max depth

## Examples

1. Scan the entire system for all large files and folders:
   ```
   ./linuxlaunder.sh
   ```

2. Scan the home directory for large media files, ignoring the Downloads folder:
   ```
   ./linuxlaunder.sh -d /home/user -s media -i Downloads
   ```

3. Scan for large document files in the /home directory with a 50MB threshold and verbose output:
   ```
   ./linuxlaunder.sh -d /home -s document -t 50 -v
   ```

4. Scan for potentially malicious files in the entire system with quiet mode:
   ```
   ./linuxlaunder.sh -s malicious -q
   ```

5. Scan the /var directory with a maximum depth of 3 and hide deep files:
   ```
   ./linuxlaunder.sh -d /var --max-depth 3 --hide-deep-files
   ```

## Interactive Selection

After scanning, LinuxLaunder presents an interactive menu for selecting items to remove:

1. Use arrow keys to navigate the tree structure.
2. Press Enter to expand/collapse folders.
3. Press Space to select/deselect items (selecting a folder selects all its contents).
4. Press 'q' to confirm your selection and proceed with removal.

The selection interface uses the following indicators:
- '[x]' for selected items (both files and folders)
- '[+]' for collapsed, unselected folders
- '[-]' for expanded, unselected folders
- '[ ]' for unselected files

## Caution

- Be careful when deleting files, folders, or uninstalling packages, especially when running the script with sudo privileges (preferably don't do this at all).
- Always double-check before confirming any deletion or uninstallation.
- Consider creating a backup before making significant changes to your system.

## Contributing

Contributions to LinuxLaunder are welcome! Please feel free to submit pull requests, report bugs, or suggest new features.

## Disclaimer

LinuxLaunder is provided as-is, without any warranties or guarantees. The authors are not responsible for any data loss or system instability resulting from the use of this tool. Always ensure you have up-to-date backups before performing any system maintenance or cleanup operations.
