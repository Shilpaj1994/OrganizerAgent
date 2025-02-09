#! /usr/bin/env python3
"""
System Tools
Author: Shilpaj Bhalerao
Date: 2025-02-08
"""

# Standard Library Imports
from typing import Dict, Union
from pathlib import Path
import sys
import shutil

# class UserInputTool(Tool):
#     name = "user_input"
#     description = "Asks for user's input on a specific question"
#     inputs = {"question": {"type": "string", "description": "The question to ask the user"}}
#     output_type = "string"

#     def forward(self, question):
#         user_input = input(f"{question} => Type your answer here:")
#         return user_input


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
