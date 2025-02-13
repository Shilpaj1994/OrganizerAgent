#! /usr/bin/env python3
"""
Internet Tools
Author: Shilpaj Bhalerao
Date: Feb 10, 2025
"""
# Standard Library Imports
import os
import requests
from typing import Optional
from pathlib import Path

def compress_pdf(pdf_path: str) -> bool:
    """
    Method which uses online service to compress the pdf file using ilovepdf API
    :param pdf_path: Path to the pdf file
    :return: True if the pdf is compressed successfully, False otherwise
    """
    try:
        # Check if file exists
        if not os.path.exists(pdf_path):
            print(f"Error: File {pdf_path} does not exist")
            return False
            
        # API endpoint for PDF compression (using ilovepdf API as an example)
        API_KEY = os.getenv('ILOVEPDF_API_KEY')
        if not API_KEY:
            print("Error: ILOVEPDF_API_KEY environment variable not set")
            return False
            
        base_url = "https://api.ilovepdf.com/v1"
        
        # Start task
        headers = {'Authorization': f'Bearer {API_KEY}'}
        response = requests.post(f"{base_url}/start/compress", headers=headers)
        if response.status_code != 200:
            print("Error starting compression task")
            return False
            
        task = response.json()
        task_id = task['task']
        
        # Upload file
        files = {'file': open(pdf_path, 'rb')}
        response = requests.post(
            f"{base_url}/upload",
            headers=headers,
            files=files,
            data={'task': task_id}
        )
        
        if response.status_code != 200:
            print("Error uploading file")
            return False
            
        server_filename = response.json()['server_filename']
        
        # Process file
        response = requests.post(
            f"{base_url}/process",
            headers=headers,
            json={
                'task': task_id,
                'tool': 'compress',
                'files': [{'server_filename': server_filename}]
            }
        )
        
        if response.status_code != 200:
            print("Error processing file")
            return False
            
        # Download result
        response = requests.get(
            f"{base_url}/download/{task_id}",
            headers=headers
        )
        
        if response.status_code != 200:
            print("Error downloading compressed file")
            return False
            
        # Save compressed file
        output_path = str(Path(pdf_path).parent / f"compressed_{Path(pdf_path).name}")
        with open(output_path, 'wb') as f:
            f.write(response.content)
            
        return True
        
    except Exception as e:
        print(f"Error compressing PDF: {str(e)}")
        return False

def compress_image(image_path: str) -> bool:
    """
    Method which uses TinyPNG API to compress the image file
    :param image_path: Path to the image file
    :return: True if the image is compressed successfully, False otherwise
    """
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            print(f"Error: File {image_path} does not exist")
            return False
            
        # API endpoint for image compression (using TinyPNG API)
        API_KEY = os.getenv('TINYPNG_API_KEY')
        if not API_KEY:
            print("Error: TINYPNG_API_KEY environment variable not set")
            return False
            
        url = "https://api.tinify.com/shrink"
        
        # Read image file
        with open(image_path, 'rb') as image_file:
            response = requests.post(
                url,
                auth=('api', API_KEY),
                data=image_file.read()
            )
        
        if response.status_code != 201:
            print("Error compressing image")
            return False
            
        # Get the compressed image URL
        compressed_url = response.json()['output']['url']
        
        # Download the compressed image
        compressed_response = requests.get(compressed_url)
        if compressed_response.status_code != 200:
            print("Error downloading compressed image")
            return False
            
        # Save compressed file
        output_path = str(Path(image_path).parent / f"compressed_{Path(image_path).name}")
        with open(output_path, 'wb') as f:
            f.write(compressed_response.content)
            
        return True
        
    except Exception as e:
        print(f"Error compressing image: {str(e)}")
        return False