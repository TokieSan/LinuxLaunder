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

# Parse command-line arguments
ARGS=()
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --directory|-d|--ignore|-i|--scan-type|-s|--threshold|-t|--max-depth)
            ARGS+=("$1" "$2")
            shift
            shift
            ;;
        --verbose|-v|--quiet|-q|--hide-deep-files)
            ARGS+=("$1")
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run the Python script with the parsed arguments
python3 "$PYTHON_SCRIPT" "${ARGS[@]}" --distro "$DISTRO"
