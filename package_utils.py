import subprocess
from typing import List, Tuple
from output_utils import print_quiet

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
