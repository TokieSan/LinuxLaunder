#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/main.py"

# Detect the Linux distribution
if [ -f /etc/arch-release ]; then
    DISTRO="arch"
elif [ -f /etc/lsb-release ]; then
    DISTRO="ubuntu"
else
    echo "Unsupported distribution. Only Arch Linux and Ubuntu are supported."
    exit 1
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if the Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Python script not found: $PYTHON_SCRIPT"
    exit 1
fi

# Check if all required Python modules are present
required_modules=("file_utils.py" "folder_utils.py" "package_utils.py" "output_utils.py" "scan_utils.py")
for module in "${required_modules[@]}"; do
    if [ ! -f "$SCRIPT_DIR/$module" ]; then
        echo "Required Python module not found: $module"
        exit 1
    fi
done

# Function to print usage information
print_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  -d, --directory DIR    Specify the directory to scan (default: /)"
    echo "  -i, --ignore DIR       Specify directories to ignore during the scan (can be used multiple times)"
    echo "  -s, --scan-type TYPE   Specify the type of scan (all, media, document, archive, temporary, package, malicious)"
    echo "  -t, --threshold SIZE   Set the size threshold in MB for reporting large files (default: 100)"
    echo "  -v, --verbose          Enable verbose output"
    echo "  -q, --quiet            Enable quiet mode (suppresses all output except results)"
    echo "      --max-depth DEPTH  Maximum depth for subfolder size checking (default: 4)"
    echo "      --hide-deep-files  Hide files in directories beyond max depth"
    echo "  -h, --help             Display this help message and exit"
}

# Parse command-line arguments
ARGS=()
IGNORE_DIRS=()
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -d|--directory)
            ARGS+=("--directory" "$2")
            shift
            shift
            ;;
        -i|--ignore)
            IGNORE_DIRS+=("$2")
            shift
            shift
            ;;
        -s|--scan-type)
            ARGS+=("--scan-type" "$2")
            shift
            shift
            ;;
        -t|--threshold)
            ARGS+=("--threshold" "$2")
            shift
            shift
            ;;
        -v|--verbose)
            ARGS+=("--verbose")
            shift
            ;;
        -q|--quiet)
            ARGS+=("--quiet")
            shift
            ;;
        --max-depth)
            ARGS+=("--max-depth" "$2")
            shift
            shift
            ;;
        --hide-deep-files)
            ARGS+=("--hide-deep-files")
            shift
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            print_usage
            exit 1
            ;;
    esac
done

# Add ignore directories to arguments
for dir in "${IGNORE_DIRS[@]}"; do
    ARGS+=("--ignore" "$dir")
done

# Run the Python script with the parsed arguments
python3 "$PYTHON_SCRIPT" "${ARGS[@]}" --distro "$DISTRO"
