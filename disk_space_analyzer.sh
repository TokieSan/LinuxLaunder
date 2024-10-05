#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/disk_space_analyzer.py"

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

# Parse command-line arguments
DIRECTORY="/"
IGNORE_DIRS=""
SCAN_TYPE="all"
THRESHOLD=100
VERBOSE=""
QUIET=""
MAX_DEPTH=4

while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -d|--directory)
            DIRECTORY="$2"
            shift
            shift
            ;;
        -i|--ignore)
            IGNORE_DIRS="$2"
            shift
            shift
            ;;
        -s|--scan-type)
            SCAN_TYPE="$2"
            shift
            shift
            ;;
        -t|--threshold)
            THRESHOLD="$2"
            shift
            shift
            ;;
        -v|--verbose)
            VERBOSE="--verbose"
            shift
            ;;
        -q|--quiet)
            QUIET="--quiet"
            shift
            ;;
        --max-depth)
            MAX_DEPTH="$2"
            shift
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run the Python script with the parsed arguments
python3 "$PYTHON_SCRIPT" \
    --directory "$DIRECTORY" \
    --ignore $IGNORE_DIRS \
    --scan-type "$SCAN_TYPE" \
    --distro "$DISTRO" \
    --threshold "$THRESHOLD" \
    --max-depth "$MAX_DEPTH" \
    $VERBOSE \
    $QUIET
