import os
from functools import lru_cache
from output_utils import print_verbose, print_quiet

@lru_cache(maxsize=None)
def get_file_size(file_path: str) -> int:
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0

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

def remove_file(file_path: str):
    try:
        os.remove(file_path)
        print_quiet(f"Deleted file: {file_path}")
    except OSError as e:
        print_quiet(f"Error deleting file {file_path}: {e}")
