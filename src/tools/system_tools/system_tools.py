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


def extract_info_from_todo(file_path: str) -> List[Tuple[str, Dict[str, str]]]:
    """
    Extracts actionable tasks from a todo.txt file.

    :param file_path: Path to the todo.txt file.
    :return: A list of tuples.  Each tuple contains:
        - The function name (str) to call.
        - A dictionary of arguments (str: str) for the function.
    """
    tasks = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                print("\n", line)
                if not line:
                    continue

                # Email Reminder
                if "Remind me to" in line and "via email" in line:
                    print("Email Reminder")
                    try:
                        # Extract the reminder message
                        reminder_text = line.split("Remind me to")[1].split("via email")[0].strip()
                        task = {
                            "recipient": "shilpajbhalerao1994@gmail.com",  # Default, can be overridden in todo.txt
                            "subject": "Reminder",
                            "body": reminder_text,
                        }
                        print(task)
                        # Extract email address if specified
                        if "via email to" in line:
                            email_part = line.split("via email to")[1].split()[0].strip()
                            if "@" in email_part:  # Basic validation that it looks like an email
                                task["recipient"] = email_part

                        tasks.append(("send_email", task))
                    except Exception as e:
                        print(f"Error parsing email reminder line: '{line}' - {e}")
                        continue

                # Calendar Event
                elif "Add a calendar invite for" in line:
                    print("Calendar Event")
                    try:
                        parts = line.split("for")[1].strip().split("and share it with")
                        date_time_str = parts[0].strip().strip('"')
                        attendees_str = parts[1].strip().strip('"') if len(parts) > 1 else ""
                        print(f"parts: {parts}" )
                        print(f"date_time_str: {date_time_str}")
                        print(f"attendees_str: {attendees_str}")

                        # Basic date/time parsing (you might need more robust parsing)
                        date_time_obj = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
                        date_str = date_time_obj.strftime("%Y-%m-%d")
                        time_str = date_time_obj.strftime("%H:%M")

                        attendees = [a.strip() for a in attendees_str.split(",") if a.strip() and "@" in a]
                        print(f"attendees: {attendees}")
                        task = {
                            "date": date_str,
                            "time": time_str,
                            "attendees": attendees,
                        }
                        print(f"task: {task}")
                        tasks.append(("add_calendar_event", task))
                    except Exception as e:
                        print(f"Error parsing calendar invite line: '{line}' - {e}")
                        continue

                # Daily Stock Update
                elif "Share the stock price for" in line and "every day at" in line:
                    try:
                        parts = line.split("for")[1].strip().split("every day at")
                        symbol = parts[0].strip()
                        time_str = parts[1].split("via email with")[0].strip()  # Extract time
                        email = parts[1].split("with")[1].strip()

                        # Basic time parsing (you might need more robust parsing)
                        # We don't actually use the time here, but we parse it to validate the format
                        datetime.strptime(time_str, "%I %p")

                        task = {
                            "symbol": symbol,
                            "recipient": email,
                        }
                        tasks.append(("send_daily_stock_update", task))

                    except Exception as e:
                        print(f"Error parsing stock update line: '{line}' - {e}")
                        continue
        print(tasks)
        return tasks

    except FileNotFoundError:
        print(f"Todo file not found: {file_path}")
        return []
    except Exception as e:
        print(f"Error reading todo file: {e}")
        return []
