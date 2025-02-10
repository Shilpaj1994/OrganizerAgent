#! /usr/bin/env python3
"""
System Tools
Author: Shilpaj Bhalerao
Date: Feb 8, 2025
"""
# Standard Library Imports
import os
import shutil
from pathlib import Path
import time

# Third Party Imports
from tqdm import tqdm
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def process_todo(todo_path):
    with open(todo_path, 'r') as f:
        for line in f:
            if 'Remind me to' in line:
                _handle_reminder(line)
            elif 'Add a calendar invite' in line:
                _handle_calendar(line)
            elif 'Share the stock price' in line:
                _schedule_stock_updates(line)

def compress_pdf(pdf_path):
    # Integration with PDF compression API
    pass

def compress_image(image_path):
    # Integration with image compression API
    pass

def _handle_reminder(task_line):
    # Email sending logic using SMTP
    pass

def _handle_calendar(task_line):
    # Calendar API integration
    pass

def _schedule_stock_updates(task_line):
    # Stock data scheduling logic
    pass





def get_directory_name() -> str:
    """
    Tool to get the directory name from the user.
    :return: The directory name
    """
    directory_name = input("Enter the directory name: ")
    return directory_name


def list_directory_files(path: str) -> list:
    """
    Tool to list all the files in the directory.
    :param path: Directory location on the local system
    :returns: List of files in the directory
    """
    try:
        dir_path = Path(path)
        if not dir_path.exists() or not dir_path.is_dir():
            return []
        return [f.name for f in dir_path.iterdir() if f.is_file()]
    except Exception as e:
        print(f"Error: {str(e)}")
        return []


def make_copy_of_file(file_path: str, new_file_path: str) -> bool:
    """
    Tool to make a copy of a file.
    :param file_path: Path to the file to be copied
    :param new_file_path: Path to the new file
    :returns: True if the file is copied successfully, False otherwise
    """
    try:
        shutil.copy(file_path, new_file_path)
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


class FileOrganizer(FileSystemEventHandler):
    def __init__(self, watch_folder):
        self.watch_folder = watch_folder
        self.categories = {
            'documents': ['.pdf', '.docx', '.txt', '.drawio', '.doc', '.rtf', '.odt', '.tex', '.md', '.pages', '.epub', '.djvu'],
            'spreadsheets': ['.xlsx', '.xls', '.csv', '.ods', '.numbers', '.tsv', '.gsheet'],
            'presentations': ['.ppt', '.pptx', '.key', '.odp', '.gslides'],
            'images': ['.jpg', '.png', '.gif', '.jpeg', '.bmp', '.tiff', '.ico', '.webp', '.svg', '.psd', '.ai', '.eps', '.raw', '.cr2', '.nef', '.heic', '.avif'],
            'code': ['.py', '.js', '.html', '.css', '.json', '.pyc', '.h', '.cpp', '.c', '.java', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.ts', '.jsx', '.vue', '.sql', '.r', '.m', '.scala', '.dart'],
            'archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso', '.dmg'],
            'notebooks': ['.ipynb', '.rmd', '.zmd'],
            'audio': ['.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.wma', '.aiff', '.opus'],
            'video': ['.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm', '.m4v', '.mpeg', '.3gp'],
            'databases': ['.db', '.sqlite', '.sqlite3', '.mdb', '.accdb', '.sql'],
            'fonts': ['.ttf', '.otf', '.woff', '.woff2', '.eot'],
            'ebooks': ['.epub', '.mobi', '.azw', '.azw3', '.fb2', '.lit'],
            'cad': ['.dwg', '.dxf', '.stl', '.obj', '.fbx', '.blend'],
            'executables': ['.exe', '.msi', '.app', '.dmg', '.deb', '.rpm']
        }
        # Process existing files when starting
        self.process_existing_files()
        
    def process_existing_files(self):
        """Process all existing files in the watch folder"""
        print("Processing existing files...")
        for item in tqdm(os.listdir(self.watch_folder), desc="Processing existing files"):
            file_path = os.path.join(self.watch_folder, item)
            if os.path.isfile(file_path):
                if item == 'todo.txt':
                    process_todo(file_path)
                else:
                    self._categorize_file(file_path)
    
    def on_created(self, event):
        """Handle new file creation events"""
        if not event.is_directory:
            print(f"New file detected: {event.src_path}")
            filename = os.path.basename(event.src_path)
            if filename == 'todo.txt':
                process_todo(event.src_path)
            else:
                self._categorize_file(event.src_path)
    
    def _categorize_file(self, file_path):
        try:
            if not os.path.exists(file_path):  # File might have been moved already
                return
                
            file_ext = Path(file_path).suffix.lower()
            
            # Don't process files that are already in category folders
            parent_dir = os.path.basename(os.path.dirname(file_path))
            if parent_dir in self.categories:
                return
                
            for category, extensions in self.categories.items():
                if file_ext in extensions:
                    print(f"Moving {file_path} to {category} folder")
                    dest_dir = os.path.join(self.watch_folder, category)
                    os.makedirs(dest_dir, exist_ok=True)
                    
                    dest_path = os.path.join(dest_dir, os.path.basename(file_path))
                    # Handle case where file already exists in destination
                    if os.path.exists(dest_path):
                        base, ext = os.path.splitext(dest_path)
                        counter = 1
                        while os.path.exists(f"{base}_{counter}{ext}"):
                            counter += 1
                        dest_path = f"{base}_{counter}{ext}"
                    
                    shutil.move(file_path, dest_path)
                    print(f"Moved {file_path} to {dest_path}")
                    
                    # Handle compression for supported formats
                    try:
                        if file_ext == '.pdf':
                            compress_pdf(dest_path)
                        elif file_ext in ['.jpg', '.png']:
                            compress_image(dest_path)
                    except Exception as e:
                        print(f"Compression error for {file_path}: {str(e)}")
                    break
        except Exception as e:
            print(f"Error categorizing {file_path}: {str(e)}")


def organize_files(path: str) -> bool:
    """
    Tool to organize the files in the directory.
    :param path: Directory location on the local system
    :returns: True if the files are organized successfully, False otherwise
    """
    try:
        print(f"Starting file organization for: {path}")
        observer = Observer()
        event_handler = FileOrganizer(path)
        observer.schedule(event_handler, path, recursive=False)  # Changed to non-recursive
        observer.start()
        print("Watching for new files...")
        
        observer.stop()
        observer.join()
        
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
