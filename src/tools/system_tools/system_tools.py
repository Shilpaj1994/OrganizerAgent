#! /usr/bin/env python3
"""
System Tools
Author: Shilpaj Bhalerao
Date: Feb 8, 2025
"""
# Standard Library Imports
import os
from pathlib import Path
import shutil
from typing import Dict, List, Set, Tuple
from datetime import datetime


def get_directory_name(default_path: str="/media/shilpaj/2A42A8EC42A8BDC7/Udacity/EPAi/Agent/experiments") -> str:
    """
    Tool to get the directory name from the user.
    :param default_path: The default path to the directory to organize
    :return: The directory name
    """
    path = input("Enter the path to the directory to organize (default: current directory): ") or default_path
    return path


def scan_directory(path: str) -> List[str]:
    """
    Scans a directory and returns a list of all files (excluding directories)
    :param path: Path to the directory to scan
    :return: List of file paths
    """
    try:
        files = []
        # Walk through directory
        for root, _, filenames in os.walk(path):
            for filename in filenames:
                # Get full file path
                file_path = os.path.join(root, filename)
                # Only include files, not directories
                if os.path.isfile(file_path):
                    files.append(file_path)
        return files
    except Exception as e:
        print(f"Error scanning directory: {str(e)}")
        return []


def identify_file_types(file_paths: List[str]) -> Dict[str, List[str]]:
    """
    Identifies and categorizes files based on their extensions
    :param file_paths: List of file paths to categorize
    :return: Dictionary mapping categories to lists of file paths
    """
    # File extension categories
    categories = {
        'documents': {'.pdf', '.docx', '.txt', '.drawio', '.doc', '.rtf', '.odt', '.tex', '.md', '.pages'},
        'spreadsheets': {'.xlsx', '.xls', '.csv', '.ods', '.numbers', '.tsv', '.gsheet'},
        'presentations': {'.ppt', '.pptx', '.key', '.odp', '.gslides'},
        'images': {'.jpg', '.png', '.gif', '.jpeg', '.bmp', '.tiff', '.ico', '.webp', '.svg', '.psd', '.ai'},
        'code': {'.py', '.js', '.html', '.css', '.json', '.pyc', '.h', '.cpp', '.c', '.java', '.go', '.rs'},
        'archives': {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso', '.dmg'},
        'audio': {'.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.wma', '.aiff'},
        'video': {'.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm', '.m4v'},
        'notebooks': {'.ipynb'}
    }

    # Initialize result dictionary
    categorized_files = {category: [] for category in categories}
    categorized_files['others'] = []  # For unrecognized file types

    try:
        for file_path in file_paths:
            file_ext = Path(file_path).suffix.lower()
            
            # Find matching category
            matched = False
            for category, extensions in categories.items():
                if file_ext in extensions:
                    categorized_files[category].append(file_path)
                    matched = True
                    break
            
            # If no category matched, add to others
            if not matched:
                categorized_files['others'].append(file_path)

        return categorized_files
    except Exception as e:
        print(f"Error identifying file types: {str(e)}")
        return categorized_files


def organize_files_by_type(categorized_files: Dict[str, List[str]], destination_path: str) -> bool:
    """
    Moves files into their respective category folders
    :param categorized_files: Dictionary mapping categories to lists of file paths
    :param destination_path: Base path where category folders will be created
    :return: True if successful, False otherwise
    """
    try:
        for category, files in categorized_files.items():
            if not files:  # Skip empty categories
                continue

            # Create category folder
            category_path = os.path.join(destination_path, category)
            os.makedirs(category_path, exist_ok=True)

            # Move files to category folder
            for file_path in files:
                # Get filename without path
                filename = os.path.basename(file_path)
                # Create destination path
                dest_path = os.path.join(category_path, filename)

                # Handle duplicate filenames
                if os.path.exists(dest_path):
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(os.path.join(category_path, f"{base}_{counter}{ext}")):
                        counter += 1
                    dest_path = os.path.join(category_path, f"{base}_{counter}{ext}")

                # Move the file
                shutil.move(file_path, dest_path)
                print(f"Moved {filename} to {category} folder")

        return True
    except Exception as e:
        print(f"Error organizing files: {str(e)}")
        return False
