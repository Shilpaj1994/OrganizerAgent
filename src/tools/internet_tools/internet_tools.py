#! /usr/bin/env python3
"""
Internet Tools
Author: Shilpaj Bhalerao
Date: Feb 10, 2025
"""
# Standard Library Imports
import base64
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import subprocess

# Third-party imports
import yfinance as yf
import pickle
import convertapi
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText


def compress_pdf(file_paths: Dict[str, List[str]]) -> bool:
    """
    Compresses a PDF file using ConvertAPI.

    :param file_paths: A dictionary with keys as the folder names and values as the file path inside the folder.
    :return: True if compression was successful, False otherwise.
    """
    try:
        # Ensure API key is set
        convertapi.api_credentials = os.getenv('CONVERT_API_KEY')
        if not convertapi.api_credentials:
            raise ValueError("Error: CONVERT_API_KEY environment variable not set!")

        if not file_paths:
            print("Warning: compress_pdf called with an empty dictionary.")
            return True  # Return True for empty dict (no-op)

        for folder, paths in file_paths.items():
            for file_path in paths:
                try:
                    if not Path(file_path).is_file():
                        print(f"Warning: '{file_path}' in folder '{folder}' is not a valid file path. Skipping.")
                        continue  # Skip invalid paths

                    # Check if file is PDF
                    if not file_path.lower().endswith('.pdf'):
                        print(f"Warning: '{file_path}' is not a PDF file. Skipping.")
                        continue

                    # Perform the compression
                    result = convertapi.convert('compress', {
                        'File': file_path  # Pass individual file path
                    }, from_format='pdf')

                    if not result or not result.files:
                        print(f"Conversion failed for {file_path} in folder '{folder}', no output files received.")
                        continue # Skip to the next file

                    # Save to a new file with '_compressed' suffix
                    output_path = str(Path(file_path).with_suffix('')) + '_compressed' + Path(file_path).suffix
                    result.file.save(output_path) # Use .file (singular)
                    print(f"Compressed: {file_path} -> {output_path}")

                except Exception as e:
                    print(f"Error compressing {file_path} in folder '{folder}': {e}")
                    return False  # Return False on any error within the loop

        return True  # Return True only if all files processed successfully

    except Exception as e:
        print(f"Error in compress_pdf: {e}")
        return False


def compress_image(file_paths: Dict[str, List[str]]) -> bool:
    """
    Compresses image files using PDFShift API.
    :param file_paths: A dictionary with keys as folder names and values as list of file paths
    :return: True if compression was successful, False otherwise
    """
    try:
        # Set API credentials
        convertapi.api_credentials = os.getenv('CONVERT_API_KEY')
        if not convertapi.api_credentials:
            raise ValueError("Error: CONVERT_API_KEY environment variable not set!")

        if not file_paths:
            print("Warning: compress_image called with an empty dictionary")
            return True

        for folder, paths in file_paths.items():
            for file_path in paths:
                try:
                    if not Path(file_path).is_file():
                        print(f"Warning: '{file_path}' in folder '{folder}' is not a valid file path. Skipping.")
                        continue

                    # Get file extension
                    file_ext = Path(file_path).suffix.lower()[1:]
                    if file_ext.lower() not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                        print(f"Warning: '{file_path}' is not a supported image format. Skipping.")
                        continue

                    # Convert using the same format for input and output
                    result = convertapi.convert(
                        file_ext,
                        {
                            'File': file_path,
                            'quality': 75
                        },
                        from_format=file_ext  # Input format
                    )

                    if not result or not result.files:
                        print(f"Conversion failed for {file_path} in folder '{folder}', no output files received.")
                        continue

                    # Save to a new file with '_compressed' suffix
                    output_path = str(Path(file_path).with_suffix('')) + '_compressed' + Path(file_path).suffix
                    result.file.save(output_path)
                    print(f"Compressed: {file_path} -> {output_path}")

                except Exception as e:
                    print(f"Error compressing {file_path} in folder '{folder}': {e}")
                    return False  # Return False on any error within the loop

        return True  # Return True only if all files processed successfully

    except Exception as e:
        print(f"Error in compress_image: {str(e)}")
        return False
    

def send_email(email_subject: str, email_body: str, recipient: str) -> bool:
    """
    Method which uses Gmail API to send an email
    :param email_subject: Subject of the email
    :param email_body: Body of the email
    :param recipient: Email address to send the email to
    :return: True if the email is sent successfully, False otherwise
    """
    try:
        # Check if credentials.json exists
        if not os.path.exists('credentials.json'):
            print("Error: credentials.json file not found. Please follow the setup instructions.")
            return False

        SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        creds = None

        # The file token.pickle stores the user's access and refresh tokens
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing credentials: {str(e)}")
                    # Delete the invalid token.pickle file
                    if os.path.exists('token.pickle'):
                        os.remove('token.pickle')
                    return False
            else:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"Error during authentication: {str(e)}")
                    print("Please make sure you've set up the OAuth consent screen and added your email as a test user")
                    return False

            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        # Create Gmail API service
        service = build('gmail', 'v1', credentials=creds)

        # Create message
        message = MIMEText(email_body)
        message['to'] = recipient
        message['subject'] = email_subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Send message
        service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        print("Email sent successfully!")
        return True

    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


def add_calendar_event(event_name: str, event_date: str, shared_with: str, event_start_time: str = "00:00", event_end_time: str = "23:59") -> bool:
    """
    Method which uses Google Calendar API to add an event to the calendar
    :param event_name: Name of the event
    :param event_date: Date of the event
    :param event_start_time: Start time of the event
    :param event_end_time: End time of the event
    :param shared_with: Email address of the person to share the event with
    :return: True if the event is added successfully, False otherwise
    """
    try:
        # Check if credentials.json exists
        if not os.path.exists('credentials.json'):
            print("Error: credentials.json file not found. Please follow the setup instructions.")
            return False

        # Define the scopes for both Gmail and Calendar
        SCOPES = [
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/calendar.events'
        ]
        creds = None

        # The file token.pickle stores the user's access and refresh tokens
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing credentials: {str(e)}")
                    # Delete the invalid token.pickle file
                    if os.path.exists('token.pickle'):
                        os.remove('token.pickle')
                    return False
            else:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"Error during authentication: {str(e)}")
                    print("Please make sure you've set up the OAuth consent screen and added your email as a test user")
                    return False

            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        # Create a Calendar API service
        service = build('calendar', 'v3', credentials=creds)

        # Parse date and times
        date_format = "%Y-%m-%d"
        time_format = "%I:%M %p"
        
        try:
            event_date_obj = datetime.strptime(event_date, date_format)
            start_time_obj = datetime.strptime(event_start_time, time_format)
            end_time_obj = datetime.strptime(event_end_time, time_format)
        except ValueError as e:
            print(f"Error parsing date/time: {str(e)}")
            print("Please use format YYYY-MM-DD for date and HH:MM AM/PM for time")
            return False

        start_datetime = event_date_obj.replace(
            hour=start_time_obj.hour,
            minute=start_time_obj.minute
        )
        end_datetime = event_date_obj.replace(
            hour=end_time_obj.hour,
            minute=end_time_obj.minute
        )

        event = {
            'summary': event_name,
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'Asia/Kolkata',  # Using IST timezone
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'Asia/Kolkata',  # Using IST timezone
            },
            'attendees': [
                {'email': shared_with},
            ],
        }

        # Add event to calendar
        event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"Event created successfully: {event.get('htmlLink')}")
        return True

    except Exception as e:
        print(f"Error adding calendar event: {str(e)}")
        return False


def send_daily_stock_update(stock_symbol: str = "NVDA", recipient: str = None, scheduled_time: str = "17:00") -> dict:
    """
    Fetch today's stock data and send it via email.
    
    :param stock_symbol: Symbol of the stock (default: NVDA)
    :param recipient: Email address to send the update to (required)
    :param scheduled_time: Time to send the update in 24-hour format (default: "17:00")
    :return: Dictionary with status code and response message
    """
    try:
        # Validate required parameters
        if not recipient:
            return {
                'statusCode': 400,
                'body': 'Recipient email is required'
            }

        # Get current time
        current_time = datetime.now()
        
        # Get stock data
        stock = yf.Ticker(stock_symbol)
        
        # Get today's data
        hist = stock.history(period="1d")
        
        if hist.empty:
            return {
                'statusCode': 404,
                'body': f"No data found for symbol {stock_symbol}"
            }
        
        # Format the email body
        current_price = hist['Close'].iloc[-1]
        open_price = hist['Open'].iloc[0]
        high_price = hist['High'].iloc[0]
        low_price = hist['Low'].iloc[0]
        volume = hist['Volume'].iloc[0]
        
        # Calculate price change and percentage
        price_change = current_price - open_price
        price_change_percent = (price_change / open_price) * 100
        
        email_body = f"""
Daily Stock Update for {stock_symbol}

Date: {current_time.strftime('%Y-%m-%d')}
Time: {current_time.strftime('%H:%M')}

Current Price: ${current_price:.2f}
Open Price: ${open_price:.2f}
High: ${high_price:.2f}
Low: ${low_price:.2f}
Volume: {volume:,}

Price Change: ${price_change:.2f} ({price_change_percent:.2f}%)

Note: All prices are in USD.
"""
        
        # Send email
        email_subject = f"Daily Stock Update - {stock_symbol} - {current_time.strftime('%Y-%m-%d %H:%M')}"
        success = send_email(email_subject, email_body, recipient)
        
        if success:
            return {
                'statusCode': 200,
                'body': 'Stock update sent successfully'
            }
        else:
            return {
                'statusCode': 500,
                'body': 'Failed to send stock update'
            }
        
    except Exception as e:
        print(f"Error sending stock update: {str(e)}")
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }


def schedule_mail(recipient: str, stock_symbol: str = "NVDA", scheduled_time: str = "17:00") -> bool:
    """
    Schedule a mail to be sent at a given time.
    :param recipient: Email address to send the update to
    :param stock_symbol: Symbol of the stock
    :param scheduled_time: Time to send the update (default: 17:00)
    :return: True if successful, False otherwise
    """
    # Start the scheduler.py in a new process
    scheduler_path = Path(__file__).parent / "scheduler.py"
    subprocess.run(["python", str(scheduler_path), "--recipient", recipient, "--stock_symbol", stock_symbol, "--scheduled_time", scheduled_time])
    return True