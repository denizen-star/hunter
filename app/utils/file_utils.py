"""File utility functions"""
import os
from pathlib import Path
import yaml


def get_project_root() -> Path:
    """Get the project root directory"""
    return Path(__file__).parent.parent.parent


def get_data_path(subfolder: str = "") -> Path:
    """Get path to data folder or subfolder"""
    root = get_project_root()
    if subfolder:
        return root / "data" / subfolder
    return root / "data"


def ensure_dir_exists(path: Path) -> Path:
    """Ensure directory exists, create if it doesn't"""
    path.mkdir(parents=True, exist_ok=True)
    return path


def sanitize_filename(filename: str) -> str:
    """Remove special characters from filename"""
    # Remove or replace special characters
    filename = ''.join(c for c in filename if c.isalnum() or c in ' -_.')
    # Replace multiple spaces with single space
    filename = ' '.join(filename.split())
    return filename


def load_yaml(file_path: Path) -> dict:
    """Load YAML file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def save_yaml(data: dict, file_path: Path) -> None:
    """Save data to YAML file"""
    ensure_dir_exists(file_path.parent)
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)


def read_text_file(file_path: Path) -> str:
    """Read text file content"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def write_text_file(content: str, file_path: Path) -> None:
    """Write content to text file"""
    ensure_dir_exists(file_path.parent)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

