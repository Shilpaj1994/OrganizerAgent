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
from googleapiclient.errors import HttpError  # Import HttpError
from email.mime.text import MIMEText
from dateutil import parser  # Import dateutil parser


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
        # Construct absolute paths
        credentials_path = Path(__file__).resolve().parent / 'credentials.json'
        token_path = Path(__file__).resolve().parent / 'token.pickle'

        # Check if credentials.json exists
        if not credentials_path.exists():
            print(f"Error: credentials.json not found at {credentials_path}.")
            return False

        # Always use combined scopes
        SCOPES = [
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/calendar',  # Include Calendar!
            'https://www.googleapis.com/auth/calendar.events'
        ]
        creds = None

        if token_path.exists():
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing credentials: {e}")
                    # No need to delete here, we'll do it on the API call
                    return False
            else:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(credentials_path), SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"Error during authentication: {e}")
                    return False

            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        service = build('gmail', 'v1', credentials=creds)
        message = MIMEText(email_body)
        message['to'] = recipient
        message['subject'] = email_subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        # --- Try/Except around API call ---
        try:
            service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
            print("Email sent successfully!")
            return True
        except HttpError as error:  # Catch HttpError specifically
            if "Insufficient Permission" in str(error):
                print(f"Error: Insufficient permissions to send email.  Deleting {token_path} and re-authenticating.")
                token_path.unlink()  # Delete the token
                return False  # Indicate failure
            else:
                print(f"An unexpected error occurred: {error}")
                return False
        # --- End Try/Except ---

    except Exception as e:
        print(f"Error in send_email: {e}")
        return False


def add_calendar_event(event_name: str, event_date: str, shared_with: str, event_start_time: str = "00:00", event_end_time: str = "23:59") -> bool:
    """
    Method which uses Google Calendar API to add an event to the calendar.
    """
    try:
        # Construct absolute paths
        credentials_path = Path(__file__).resolve().parent / 'credentials.json'
        token_path = Path(__file__).resolve().parent / 'token.pickle'

        if not credentials_path.exists():
            print(f"Error: credentials.json not found at {credentials_path}.")
            return False

        # Always use combined scopes
        SCOPES = [
            'https://www.googleapis.com/auth/gmail.send',  # Include Gmail!
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/calendar.events'
        ]
        creds = None

        if token_path.exists():
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing credentials: {e}")
                     # No need to delete here, we'll do it on the API call
                    return False
            else:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(credentials_path), SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"Error during authentication: {e}")
                    return False

            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        service = build('calendar', 'v3', credentials=creds)
        time_format = "%I:%M %p"

        try:
            event_date_obj = parser.parse(event_date)
            start_time_obj = datetime.strptime(event_start_time, time_format)
            end_time_obj = datetime.strptime(event_end_time, time_format)
        except ValueError as e:
            print(f"Error parsing date/time: {e}")
            return False

        start_datetime = event_date_obj.replace(hour=start_time_obj.hour, minute=start_time_obj.minute)
        end_datetime = event_date_obj.replace(hour=end_time_obj.hour, minute=end_time_obj.minute)

        event = {
            'summary': event_name,
            'start': {'dateTime': start_datetime.isoformat(), 'timeZone': 'Asia/Kolkata'},
            'end': {'dateTime': end_datetime.isoformat(), 'timeZone': 'Asia/Kolkata'},
            'attendees': [{'email': shared_with}],
        }

        # --- Try/Except around API call ---
        try:
            event = service.events().insert(calendarId='primary', body=event).execute()
            print(f"Event created successfully: {event.get('htmlLink')}")
            return True
        except HttpError as error:  # Catch HttpError specifically
            if "Insufficient Permission" in str(error):
                print(f"Error: Insufficient permissions to add calendar event. Deleting {token_path} and re-authenticating.")
                token_path.unlink()  # Delete the token
                return False  # Indicate failure
            else:
                print(f"An unexpected error occurred: {error}")
                return False
        # --- End Try/Except ---

    except Exception as e:
        print(f"Error in add_calendar_event: {e}")
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


def schedule_daily_stock_update(recipient: str, stock_symbol: str = "NVDA", scheduled_time: str = "17:00") -> bool:
    """
    Schedule a daily stock update to be sent at a given time.
    :param recipient: Email address to send the update to
    :param stock_symbol: Symbol of the stock
    :param scheduled_time: Time to send the update (default: 17:00)
    :return: True if successful, False otherwise
    """
    # Start the scheduler.py in a new process
    scheduler_path = Path(__file__).parent / "scheduler.py"
    subprocess.Popen(["python", str(scheduler_path), "--recipient", recipient, "--stock_symbol", stock_symbol, "--scheduled_time", scheduled_time], start_new_session=True)
    return True